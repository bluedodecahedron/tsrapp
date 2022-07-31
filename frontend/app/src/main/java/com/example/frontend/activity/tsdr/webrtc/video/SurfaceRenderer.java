package com.example.frontend.activity.tsdr.webrtc.video;

import android.content.Context;
import android.util.AttributeSet;

import org.webrtc.SurfaceViewRenderer;
import org.webrtc.VideoFrame;

public class SurfaceRenderer extends SurfaceViewRenderer {
    private String TAG;
    private StatisticsRenderer statsRenderer;

    public SurfaceRenderer(Context context) {
        super(context);
    }

    public SurfaceRenderer(Context context, AttributeSet attrs) {
        super(context, attrs);
    }

    public void setTAG(String TAG) {
        this.TAG = TAG;
    }

    public void setStatsRenderer(StatisticsRenderer statsRenderer) {
        this.statsRenderer = statsRenderer;
    }

    @Override
    public void onFrame(VideoFrame frame) {
        //Log.d(TAG, "New SurfaceView frame");
        if(statsRenderer != null) {
            statsRenderer.incrementFrameCounter();
            if(statsRenderer.isUpdate()) {
                statsRenderer.update();
            }
        }
        super.onFrame(frame);
    }
}
