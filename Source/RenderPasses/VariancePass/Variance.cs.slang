/***************************************************************************
 # Copyright (c) 2015-23, NVIDIA CORPORATION. All rights reserved.
 #
 # Redistribution and use in source and binary forms, with or without
 # modification, are permitted provided that the following conditions
 # are met:
 #  * Redistributions of source code must retain the above copyright
 #    notice, this list of conditions and the following disclaimer.
 #  * Redistributions in binary form must reproduce the above copyright
 #    notice, this list of conditions and the following disclaimer in the
 #    documentation and/or other materials provided with the distribution.
 #  * Neither the name of NVIDIA CORPORATION nor the names of its
 #    contributors may be used to endorse or promote products derived
 #    from this software without specific prior written permission.
 #
 # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS "AS IS" AND ANY
 # EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 # IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 # PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 # CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 # EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 # PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 # PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
 # OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 # (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 # OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 **************************************************************************/

/**
 * Temporal accumulation render pass.
 *
 * There are entry points for each of the three supported accumulation modes.
 * Note that for the compensated summation mode the shader _must_ be compiled
 * for precise floating-point operations (no reordering).
 *
 * In all modes, the shader writes the current accumulated average to the
 * output texture. The intermediate buffers are internal to the pass.
 */
import Utils.Math.MathHelpers;

cbuffer PerFrameCB
{
    uint2 gResolution;
    uint gAccumCount;
    bool gAccumulate;
    bool gMovingAverageMode;
}

// Input data to accumulate and accumulated output.
#define INPUT_FORMAT_FLOAT 0
#define INPUT_FORMAT_UINT 1
#define INPUT_FORMAT_SINT 2

#if _INPUT_FORMAT == INPUT_FORMAT_FLOAT
typedef float4 InputDataType;
#elif _INPUT_FORMAT == INPUT_FORMAT_UINT
typedef uint4 InputDataType;
#elif _INPUT_FORMAT == INPUT_FORMAT_SINT
typedef int4 InputDataType;
#else
#error "Invalid format"
#endif

Texture2D<InputDataType> gCurFrame;
Texture2D<InputDataType> gCurDiffuse;
Texture2D<InputDataType> gCurSpecRough;
RWTexture2D<float4> gOutputFrame;
RWTexture2D<float4> gOutMean;
RWTexture2D<float2> gOutMoment;
RWTexture2D<float4> gOutVariance;
RWTexture2D<float4> gOutDemodul;

// Last frame data, format depends on accumulation mode.
RWTexture2D<float4> gLastFrameSum;  // If mode is Single or SingleKahan
RWTexture2D<float4> gLastFrameCorr; // If mode is SingleKahan
RWTexture2D<uint4> gLastFrameSumLo; // If mode is Double
RWTexture2D<uint4> gLastFrameSumHi; // If mode is Double
RWTexture2D<float4> gLastFrameMean;
RWTexture2D<float2> gLastFrameMoment;
RWTexture2D<float4> gLastFrameVariance;

float3 demodulate(float3 c, float3 albedo)
{
    float3 ret;
    bool3 zeroAlbedo = albedo == 0.0f;

    if (zeroAlbedo.x) ret.x = c.x;
    else ret.x = c.x / max(albedo.x, 0.001f);
    if (zeroAlbedo.y) ret.y = c.y;
    else ret.y = c.y / max(albedo.y, 0.001f);
    if (zeroAlbedo.z) ret.z = c.z;
    else ret.z = c.z / max(albedo.z, 0.001f);

    return ret;
}

float luminance(float3 rgb)
{
    return dot(rgb, float3(0.2126f, 0.7152f, 0.0722f));
}

/**
 * Single precision standard summation.
 */
[numthreads(16, 16, 1)]
void accumulateSingle(uint3 dispatchThreadId: SV_DispatchThreadID)
{
    if (any(dispatchThreadId.xy >= gResolution))
        return;
    const uint2 pixelPos = dispatchThreadId.xy;
    const float4 curColor = gCurFrame[pixelPos];

    const float3 albedo = gCurDiffuse[pixelPos].rgb + gCurSpecRough[pixelPos].rgb;
    const float3 illumination = demodulate(curColor.rgb, albedo);
    const float curLuminance = luminance(illumination);

    float4 output;
    float4 outMean;
    float2 outMoment;
    float4 outVariance;
    if (gAccumulate)
    {
        float curWeight = 1.0 / (gAccumCount + 1);
        int sample_cnt = gAccumCount + 1;

        if (gMovingAverageMode)
        {
            // Exponential weighted moving average mode.
            // Blend the accumulated frame with the current frame.
            output = lerp(gLastFrameSum[pixelPos], curColor, curWeight);

            gLastFrameSum[pixelPos] = output;
        }
        else
        {
            // High precision mode with no frame limit.
            // Fetch previous sum and compute the new sum.
            float4 sum = gLastFrameSum[pixelPos] + curColor;
            float mean = ((gLastFrameMean[pixelPos].x * (sample_cnt - 1)) + curLuminance) / sample_cnt; // online update sample mean and variance
            float second_moment = ((gLastFrameMoment[pixelPos].y * (sample_cnt - 1)) + (curLuminance * curLuminance)) / sample_cnt;
            //float variance = (sample_cnt / max(1, (sample_cnt - 1))) * (((sample_cnt - 1) / sample_cnt) * gLastFrameVariance[pixelPos].x) + (sqr(curLuminance - mean) / max(1, (sample_cnt - 1)));
            float variance = (((sample_cnt - 2) * gLastFrameVariance[pixelPos].x) + ((curLuminance - gLastFrameMean[pixelPos].x) * (curLuminance - mean))) / max(1, (sample_cnt - 1));

            output = sum * curWeight;
            gLastFrameSum[pixelPos] = sum;

            outMean = float4(mean, mean, mean, 0);
            outMoment = float2(mean, second_moment);
            outVariance = float4(variance, variance, variance, 0);
            gLastFrameMean[pixelPos] = outMean;
            gLastFrameMoment[pixelPos] = outMoment;
            gLastFrameVariance[pixelPos] = outVariance;
        }
    }
    else
    {
        output = curColor;
        outMean = float4(0.f,0.f,0.f,0.f);
        outMoment = float2(0.f,0.f);
        outVariance = float4(0.f,0.f,0.f,0.f);
    }

    gOutputFrame[pixelPos] = output;
    gOutDemodul[pixelPos] = float4(demodulate(float3(output.x, output.y, output.z), albedo), 0.f);
    gOutMean[pixelPos] = outMean;
    gOutMoment[pixelPos] = outMoment;
    gOutVariance[pixelPos] = outVariance;
}

/**
 * Single precision compensated summation.
 */
[numthreads(16, 16, 1)]
void accumulateSingleCompensated(uint3 dispatchThreadId: SV_DispatchThreadID)
{
    if (any(dispatchThreadId.xy >= gResolution))
        return;
    const uint2 pixelPos = dispatchThreadId.xy;
    const float4 curColor = gCurFrame[pixelPos];

    float4 output;
    if (gAccumulate)
    {
        // Fetch the previous sum and running compensation term.
        float4 sum = gLastFrameSum[pixelPos];
        // c measures how large (+) or small (-) the current sum is compared to what it should be.
        float4 c = gLastFrameCorr[pixelPos];

        // Adjust current value to minimize the running error.
        // Compute the new sum by adding the adjusted current value.
        float4 y = curColor - c;
        // The value we'll see in 'sum' on the next iteration.
        float4 sumNext = sum + y;
        output = sumNext / (gAccumCount + 1);

        gLastFrameSum[pixelPos] = sumNext;
        // Store new correction term.
        gLastFrameCorr[pixelPos] = (sumNext - sum) - y;
    }
    else
    {
        output = curColor;
    }

    gOutputFrame[pixelPos] = output;
}

/**
 * Double precision standard summation.
 */
[numthreads(16, 16, 1)]
void accumulateDouble(uint3 dispatchThreadId: SV_DispatchThreadID)
{
    if (any(dispatchThreadId.xy >= gResolution))
        return;
    const uint2 pixelPos = dispatchThreadId.xy;
    const float4 curColor = gCurFrame[pixelPos];

    float4 output;
    if (gAccumulate)
    {
        double curWeight = 1.0 / (gAccumCount + 1);

        // Fetch the previous sum in double precision.
        // There is no 'double' resource format, so the bits are stored in two uint4 textures.
        uint4 sumLo = gLastFrameSumLo[pixelPos];
        uint4 sumHi = gLastFrameSumHi[pixelPos];

        double sum[4];

        if (gMovingAverageMode)
        {
            // Exponential weighted moving average mode.
            for (int i = 0; i < 4; i++)
            {
                sum[i] = asdouble(sumLo[i], sumHi[i]);
                sum[i] = sum[i] * (1.0 - curWeight) + (double)curColor[i] * curWeight;
                asuint(sum[i], sumLo[i], sumHi[i]);
                output[i] = (float)sum[i];
            }
        }
        else
        {
            // High precision mode with no frame limit.
            for (int i = 0; i < 4; i++)
            {
                sum[i] = asdouble(sumLo[i], sumHi[i]);
                sum[i] += (double)curColor[i];
                asuint(sum[i], sumLo[i], sumHi[i]);
                output[i] = (float)(sum[i] * curWeight);
            }
        }

        gLastFrameSumLo[pixelPos] = sumLo;
        gLastFrameSumHi[pixelPos] = sumHi;
    }
    else
    {
        output = curColor;
    }

    gOutputFrame[pixelPos] = output;
}
