package com.example.frontend.activity.tsdr.webrtc.encoder;

import static com.example.frontend.activity.tsdr.webrtc.encoder.CustomMediaCodecUtils.EXYNOS_PREFIX;
import static com.example.frontend.activity.tsdr.webrtc.encoder.CustomMediaCodecUtils.INTEL_PREFIX;
import static com.example.frontend.activity.tsdr.webrtc.encoder.CustomMediaCodecUtils.QCOM_PREFIX;
import static com.example.frontend.activity.tsdr.webrtc.encoder.CustomMediaCodecUtils.SOFTWARE_IMPLEMENTATION_PREFIXES;

import android.media.MediaCodecInfo;
import android.media.MediaCodecList;
import android.os.Build;

import androidx.annotation.Nullable;

import org.apache.commons.lang3.StringUtils;
import org.webrtc.EglBase;
import org.webrtc.EglBase14;
import org.webrtc.HardwareVideoEncoderFactory;
import org.webrtc.Logging;
import org.webrtc.Predicate;
import org.webrtc.VideoCodecInfo;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class CustomHardwareVideoEncoderFactory extends HardwareVideoEncoderFactory {
    private static final String TAG = CustomHardwareVideoEncoderFactory.class.getSimpleName();

    // Forced key frame interval - used to reduce color distortions on Qualcomm platforms.
    private static final int QCOM_VP8_KEY_FRAME_INTERVAL_ANDROID_L_MS = 15000;
    private static final int QCOM_VP8_KEY_FRAME_INTERVAL_ANDROID_M_MS = 20000;
    private static final int QCOM_VP8_KEY_FRAME_INTERVAL_ANDROID_N_MS = 15000;

    // List of devices with poor H.264 encoder quality.
    // HW H.264 encoder on below devices has poor bitrate control - actual
    // bitrates deviates a lot from the target value.
    private static final List<String> H264_HW_EXCEPTION_MODELS =
            Arrays.asList("SAMSUNG-SGH-I337", "Nexus 7", "Nexus 4");

    private final boolean enableIntelVp8Encoder;
    private final boolean enableH264HighProfile;

    public CustomHardwareVideoEncoderFactory(EglBase.Context sharedContext, boolean enableIntelVp8Encoder, boolean enableH264HighProfile) {
        super(sharedContext, enableIntelVp8Encoder, enableH264HighProfile);
        this.enableIntelVp8Encoder = enableIntelVp8Encoder;
        this.enableH264HighProfile = enableH264HighProfile;
    }

    public CustomHardwareVideoEncoderFactory(EglBase.Context sharedContext, boolean enableIntelVp8Encoder, boolean enableH264HighProfile, Predicate<MediaCodecInfo> codecAllowedPredicate) {
        super(sharedContext, enableIntelVp8Encoder, enableH264HighProfile, codecAllowedPredicate);
        this.enableIntelVp8Encoder = enableIntelVp8Encoder;
        this.enableH264HighProfile = enableH264HighProfile;
    }

    public CustomHardwareVideoEncoderFactory(boolean enableIntelVp8Encoder, boolean enableH264HighProfile) {
        super(enableIntelVp8Encoder, enableH264HighProfile);
        this.enableIntelVp8Encoder = enableIntelVp8Encoder;
        this.enableH264HighProfile = enableH264HighProfile;
    }
    
    @Override
    public VideoCodecInfo[] getSupportedCodecs() {
        // HW encoding is not supported below Android Kitkat.
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.KITKAT) {
            return new VideoCodecInfo[0];
        }
        List<VideoCodecInfo> supportedCodecInfos = new ArrayList<VideoCodecInfo>();
        // Generate a list of supported codecs in order of preference:
        // VP8, VP9, H264 (high profile), H264 (baseline profile) and AV1.
        for (CustomVideoCodecMimeType type : new CustomVideoCodecMimeType[] {
                CustomVideoCodecMimeType.VP8,
                CustomVideoCodecMimeType.H264,
                CustomVideoCodecMimeType.VP9,
                CustomVideoCodecMimeType.AV1
        }) {
            MediaCodecInfo codec = findCodecForType(type);
            if (codec != null) {
                String name = type.toSdpCodecName();
                // TODO(sakal): Always add H264 HP once WebRTC correctly removes codecs that are not
                // supported by the decoder.
                if (type == CustomVideoCodecMimeType.H264 && isH264HighProfileSupported(codec)) {
                    supportedCodecInfos.add(new VideoCodecInfo(
                            name, CustomMediaCodecUtils.getCodecProperties(type, /* highProfile= */ true)));
                }
                supportedCodecInfos.add(new VideoCodecInfo(
                        name, CustomMediaCodecUtils.getCodecProperties(type, /* highProfile= */ false)));
            }
        }
        return supportedCodecInfos.toArray(new VideoCodecInfo[supportedCodecInfos.size()]);
    }

    private @Nullable MediaCodecInfo findCodecForType(CustomVideoCodecMimeType type) {
        for (int i = 0; i < MediaCodecList.getCodecCount(); ++i) {
            MediaCodecInfo info = null;
            try {
                info = MediaCodecList.getCodecInfoAt(i);
            } catch (IllegalArgumentException e) {
                Logging.e(TAG, "Cannot retrieve encoder codec info", e);
            }
            if (info == null || !info.isEncoder()) {
                continue;
            }
            if (isSupportedCodec(info, type)) {
                return info;
            }
        }
        return null; // No support for this type.
    }

    // Returns true if the given MediaCodecInfo indicates a supported encoder for the given type.
    private boolean isSupportedCodec(MediaCodecInfo info, CustomVideoCodecMimeType type) {
        if (!CustomMediaCodecUtils.codecSupportsType(info, type)) {
            return false;
        }
        // Check for a supported color format.
        if (CustomMediaCodecUtils.selectColorFormat(
                CustomMediaCodecUtils.ENCODER_COLOR_FORMATS, info.getCapabilitiesForType(type.mimeType()))
                == null) {
            return false;
        }
        return isHardwareSupportedInCurrentSdk(info, type);
    }

    // Returns true if the given MediaCodecInfo indicates a hardware module that is supported on the
    // current SDK.
    private boolean isHardwareSupportedInCurrentSdk(MediaCodecInfo info, CustomVideoCodecMimeType type) {
        switch (type) {
            case VP8:
                return isHardwareSupportedInCurrentSdkVp8(info);
            case VP9:
                return isHardwareSupportedInCurrentSdkVp9(info);
            case H264:
                return isHardwareSupportedInCurrentSdkH264(info);
            case AV1:
                return false;
        }
        return false;
    }

    private boolean isHardwareSupportedInCurrentSdkVp8(MediaCodecInfo info) {
        String name = info.getName();
        // QCOM Vp8 encoder is supported in KITKAT or later.
        return (name.startsWith(QCOM_PREFIX) && Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT)
                // Exynos VP8 encoder is supported in M or later.
                || (name.startsWith(EXYNOS_PREFIX) && Build.VERSION.SDK_INT >= Build.VERSION_CODES.M)
                // Intel Vp8 encoder is supported in LOLLIPOP or later, with the intel encoder enabled.
                || (name.startsWith(INTEL_PREFIX) && Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP
                && enableIntelVp8Encoder);
    }

    private boolean isHardwareSupportedInCurrentSdkVp9(MediaCodecInfo info) {
        String name = info.getName();
        return (name.startsWith(QCOM_PREFIX) || name.startsWith(EXYNOS_PREFIX))
                // Both QCOM and Exynos VP9 encoders are supported in N or later.
                && Build.VERSION.SDK_INT >= Build.VERSION_CODES.N;
    }

    private boolean isHardwareSupportedInCurrentSdkH264(MediaCodecInfo info) {
        // First, H264 hardware might perform poorly on this model.
        if (H264_HW_EXCEPTION_MODELS.contains(Build.MODEL)) {
            return false;
        }
        String name = info.getName();
        for (String prefix : SOFTWARE_IMPLEMENTATION_PREFIXES) {
            if (name.startsWith(prefix)) {
                return false;
            }
        }
        return true;
        // QCOM H264 encoder is supported in KITKAT or later.
        //return (name.startsWith(QCOM_PREFIX) && Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT)
        //        // Exynos H264 encoder is supported in LOLLIPOP or later.
        //        || (name.startsWith(EXYNOS_PREFIX)
        //        && Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP);
    }

    private int getKeyFrameIntervalSec(CustomVideoCodecMimeType type) {
        switch (type) {
            case VP8: // Fallthrough intended.
            case VP9:
            case AV1:
                return 100;
            case H264:
                return 20;
        }
        throw new IllegalArgumentException("Unsupported CustomVideoCodecMimeType " + type);
    }

    private int getForcedKeyFrameIntervalMs(CustomVideoCodecMimeType type, String codecName) {
        if (type == CustomVideoCodecMimeType.VP8 && codecName.startsWith(QCOM_PREFIX)) {
            if (Build.VERSION.SDK_INT == Build.VERSION_CODES.LOLLIPOP
                    || Build.VERSION.SDK_INT == Build.VERSION_CODES.LOLLIPOP_MR1) {
                return QCOM_VP8_KEY_FRAME_INTERVAL_ANDROID_L_MS;
            } else if (Build.VERSION.SDK_INT == Build.VERSION_CODES.M) {
                return QCOM_VP8_KEY_FRAME_INTERVAL_ANDROID_M_MS;
            } else if (Build.VERSION.SDK_INT > Build.VERSION_CODES.M) {
                return QCOM_VP8_KEY_FRAME_INTERVAL_ANDROID_N_MS;
            }
        }
        // Other codecs don't need key frame forcing.
        return 0;
    }

    private CustomBitrateAdjuster createBitrateAdjuster(CustomVideoCodecMimeType type, String codecName) {
        if (codecName.startsWith(EXYNOS_PREFIX)) {
            if (type == CustomVideoCodecMimeType.VP8) {
                // Exynos VP8 encoders need dynamic bitrate adjustment.
                return new CustomDynamicBitrateAdjuster();
            } else {
                // Exynos VP9 and H264 encoders need framerate-based bitrate adjustment.
                return new CustomFramerateBitrateAdjuster();
            }
        }
        // Other codecs don't need bitrate adjustment.
        return new CustomBaseBitrateAdjuster();
    }

    private boolean isH264HighProfileSupported(MediaCodecInfo info) {
        return enableH264HighProfile && Build.VERSION.SDK_INT > Build.VERSION_CODES.M
                && info.getName().startsWith(EXYNOS_PREFIX);
    }
}
