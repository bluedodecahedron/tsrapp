package com.example.frontend.schema;

public class Offer {
    String sdp;
    String type;
    String video_transform;

    public Offer(String sdp, String type, String video_transform) {
        this.sdp = sdp;
        this.type = type;
        this.video_transform = video_transform;
    }

    public String getSdp() {
        return sdp;
    }

    public void setSdp(String sdp) {
        this.sdp = sdp;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public String getVideo_transform() {
        return video_transform;
    }

    public void setVideo_transform(String video_transform) {
        this.video_transform = video_transform;
    }
}
