/*
 *  Copyright 2017 The WebRTC project authors. All Rights Reserved.
 *
 *  Use of this source code is governed by a BSD-style license
 *  that can be found in the LICENSE file in the root of the source
 *  tree. An additional intellectual property rights grant can be found
 *  in the file PATENTS.  All contributing project authors may
 *  be found in the AUTHORS file in the root of the source tree.
 */
package com.example.frontend.activity.tsdr.webrtc.encoder;
import android.media.MediaCodecInfo;

import androidx.annotation.Nullable;

import org.webrtc.VideoCodecInfo;

import java.util.HashMap;
import java.util.Map;

class CustomMediaCodecUtils {
    // Prefixes for supported hardware encoder/decoder component names.
    static final String EXYNOS_PREFIX = "OMX.Exynos.";
    static final String INTEL_PREFIX = "OMX.Intel.";
    static final String NVIDIA_PREFIX = "OMX.Nvidia.";
    static final String QCOM_PREFIX = "OMX.qcom.";
    static final String[] SOFTWARE_IMPLEMENTATION_PREFIXES = {
            "OMX.google.", "OMX.SEC.", "c2.android"};

    static final int COLOR_QCOM_FORMATYUV420PackedSemiPlanar32m = 0x7FA30C04;
    static final int[] ENCODER_COLOR_FORMATS = {
            MediaCodecInfo.CodecCapabilities.COLOR_FormatYUV420Planar,
            MediaCodecInfo.CodecCapabilities.COLOR_FormatYUV420SemiPlanar,
            MediaCodecInfo.CodecCapabilities.COLOR_QCOM_FormatYUV420SemiPlanar,
            CustomMediaCodecUtils.COLOR_QCOM_FORMATYUV420PackedSemiPlanar32m};

    static Map<String, String> getCodecProperties(CustomVideoCodecMimeType type, boolean highProfile) {
        switch (type) {
            case VP8:
            case VP9:
            case AV1:
                return new HashMap<String, String>();
            case H264:
                return getDefaultH264Params(highProfile);
            default:
                throw new IllegalArgumentException("Unsupported codec: " + type);
        }
    }

    public static Map<String, String> getDefaultH264Params(boolean isHighProfile) {
        final Map<String, String> params = new HashMap<>();
        params.put(VideoCodecInfo.H264_FMTP_LEVEL_ASYMMETRY_ALLOWED, "1");
        params.put(VideoCodecInfo.H264_FMTP_PACKETIZATION_MODE, "1");
        params.put(VideoCodecInfo.H264_FMTP_PROFILE_LEVEL_ID,
                isHighProfile ? VideoCodecInfo.H264_CONSTRAINED_HIGH_3_1
                        : VideoCodecInfo.H264_CONSTRAINED_BASELINE_3_1);
        return params;
    }

    static boolean codecSupportsType(MediaCodecInfo info, CustomVideoCodecMimeType type) {
        for (String mimeType : info.getSupportedTypes()) {
            if (type.mimeType().equals(mimeType)) {
                return true;
            }
        }
        return false;
    }

    static @Nullable Integer selectColorFormat(int[] supportedColorFormats, MediaCodecInfo.CodecCapabilities capabilities) {
        for (int supportedColorFormat : supportedColorFormats) {
            for (int codecColorFormat : capabilities.colorFormats) {
                if (codecColorFormat == supportedColorFormat) {
                    return codecColorFormat;
                }
            }
        }
        return null;
    }

}