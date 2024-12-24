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
#pragma once
#include "Falcor.h"
#include "RenderGraph/RenderPass.h"
#include "Utils/glm/glm.hpp"
#include "Utils/glm/mat4x4.hpp"


using namespace Falcor;

class CapturePass : public RenderPass
{
public:
    FALCOR_PLUGIN_CLASS(CapturePass, "CapturePass", "Insert pass description here.");

    static ref<CapturePass> create(ref<Device> pDevice, const Properties& props)
    {
        return make_ref<CapturePass>(pDevice, props);
    }

    CapturePass(ref<Device> pDevice, const Properties& props);

    virtual Properties getProperties() const override;
    virtual RenderPassReflection reflect(const CompileData& compileData) override;
    virtual void compile(RenderContext* pRenderContext, const CompileData& compileData) override {}
    virtual void execute(RenderContext* pRenderContext, const RenderData& renderData) override;
    virtual void renderUI(Gui::Widgets& widget) override;
    virtual void setScene(RenderContext* pRenderContext, const ref<Scene>& pScene) override;
    virtual bool onMouseEvent(const MouseEvent& mouseEvent) override { return false; }
    virtual bool onKeyEvent(const KeyboardEvent& keyEvent) override { return false; }

private:
    uint32_t mLoadCount = 0; // global frame counter starts from 1
    uint32_t mStartFrame = 0; // start frame index set by user
    //std::string mDirectory;
    std::vector<std::string> mFilenames;

    std::vector<std::string> mChannels;
    std::vector<std::string> mIncludeAlpha;
    std::string mDirectory;

    ref<Scene> mpScene;

    bool mStart = true;
    bool mExitAtEnd = true;

    bool mAccumulateSubFrames = false;
    int mAccumulateCount = 16;
    int mCountSubFrame = 0;
    // std::vector<int> mWriteTarget{59, 60, 61};
    std::vector<int> mWriteTarget;
    int mWriteStart = 0, mWriteEnd = 361;
    uint32_t mFramerate = 30;
    uint64_t mCaptureCount = 0; // global frame counter starts from 1

    // Camera matrix
    bool mCaptureCameraMat = false;
    bool mCaptureCameraMatOnly = false;
    std::vector<float4x4> mCameraMatrices;
    std::vector<float4x4> mViewProjMatrices;
    std::vector<float4x4> mProjMatrices;
    float3 mCameraPosition;
    float3 mCameraTarget;
    float3 mCameraUp;
    std::string mCameraMatTemplate;
};
