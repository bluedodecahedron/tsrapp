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

/** Enumeration of supported video codec types. */
enum CustomVideoCodecMimeType {
    VP8("video/x-vnd.on2.vp8"),
    VP9("video/x-vnd.on2.vp9"),
    H264("video/avc"),
    AV1("video/av01");

    private final String mimeType;

    private CustomVideoCodecMimeType(String mimeType) {
        this.mimeType = mimeType;
    }

    String mimeType() {
        return mimeType;
    }

    static CustomVideoCodecMimeType fromSdpCodecName(String codecName) {
        return codecName.equals("AV1X") ? AV1 : valueOf(codecName);
    }

    String toSdpCodecName() {
        return this == AV1 ? "AV1X" : name();
    }
}