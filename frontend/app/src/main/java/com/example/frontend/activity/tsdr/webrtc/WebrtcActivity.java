package com.example.frontend.activity.tsdr.webrtc;

import android.Manifest;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.databinding.DataBindingUtil;

import com.example.frontend.R;
import com.example.frontend.databinding.ActivityMainBinding;
import com.example.frontend.databinding.ActivityWebrtcBinding;
import com.example.frontend.schema.Offer;
import com.example.frontend.service.OfferService;

import org.webrtc.Camera1Enumerator;
import org.webrtc.Camera2Enumerator;
import org.webrtc.CameraEnumerator;
import org.webrtc.DefaultVideoDecoderFactory;
import org.webrtc.DefaultVideoEncoderFactory;
import org.webrtc.EglBase;
import org.webrtc.MediaConstraints;
import org.webrtc.PeerConnection;
import org.webrtc.PeerConnectionFactory;
import org.webrtc.RTCStats;
import org.webrtc.RTCStatsCollectorCallback;
import org.webrtc.RTCStatsReport;
import org.webrtc.SessionDescription;
import org.webrtc.SurfaceTextureHelper;
import org.webrtc.VideoCapturer;
import org.webrtc.VideoDecoderFactory;
import org.webrtc.VideoEncoderFactory;
import org.webrtc.VideoSource;
import org.webrtc.VideoTrack;

import java.math.BigInteger;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Map;

import pub.devrel.easypermissions.AfterPermissionGranted;
import pub.devrel.easypermissions.EasyPermissions;
import retrofit2.Response;

public class WebrtcActivity extends AppCompatActivity {
    private static final String TAG = WebrtcActivity.class.getSimpleName();
    private static final int RC_CALL = 120;
    public static final String VIDEO_TRACK_ID = "ARDAMSv0";
    public static final int VIDEO_RESOLUTION_WIDTH = 720;
    public static final int VIDEO_RESOLUTION_HEIGHT = 480;
    public static final int FPS = 60;

    private ActivityWebrtcBinding binding;
    private PeerConnection localPeerConnection;
    private EglBase rootEglBase;
    private PeerConnectionFactory factory;
    private VideoTrack videoTrackFromCamera;

    private BigInteger bytesSent = BigInteger.ZERO;
    private BigInteger bytesReceived = BigInteger.ZERO;
    private LocalDateTime lastBandwidthUpdate = LocalDateTime.now();


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = DataBindingUtil.setContentView(this, R.layout.activity_webrtc);
        setSupportActionBar(binding.toolbar);

        start();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        EasyPermissions.onRequestPermissionsResult(requestCode, permissions, grantResults, this);
    }

    @AfterPermissionGranted(RC_CALL)
    private void start() {
        String[] perms = {Manifest.permission.CAMERA, Manifest.permission.INTERNET};
        Log.i(TAG, "Checking Permissions");
        if (EasyPermissions.hasPermissions(this, perms)) {
            initializeSurfaceViews();

            initializePeerConnectionFactory();

            createVideoTrackFromCameraAndShowIt();

            initializePeerConnections();

            startStreamingVideo();
        } else {
            Log.i(TAG, "Requesting Permissions");
            EasyPermissions.requestPermissions(this, "Need some permissions", RC_CALL, perms);
        }
    }

    private void initializeSurfaceViews() {
        Log.i(TAG, "Initializing Surface Views");
        rootEglBase = EglBase.create();

        binding.surfaceView2.init(rootEglBase.getEglBaseContext(), null);
        //binding.surfaceView2.setScalingType(RendererCommon.ScalingType.SCALE_ASPECT_FILL); //NEW
        binding.surfaceView2.setEnableHardwareScaler(true);
        binding.surfaceView2.setMirror(false);
        binding.surfaceView2.setTAG(TAG);
        binding.surfaceView2.setUpdateFpsUi(this::updateFpsUi);
        binding.surfaceView2.setUpdateBandwithUi(this::updateBandwidthUi);

        Log.i(TAG, "Initialized surface views");
        //add one more
    }

    private void updateFpsUi(Float fps) {
        //runOnUiThread because only the original thread that created a view hierarchy can touch its views
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                binding.fpsCounter.setText(getString(R.string.fps_counter, fps));
            }
        });
    }

    private void updateBandwidthUi() {
        //runOnUiThread because only the original thread that created a view hierarchy can touch its views
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                localPeerConnection.getStats(new RTCStatsCollectorCallback() {
                    @Override
                    public void onStatsDelivered(RTCStatsReport rtcStatsReport) {
                        Map<String, RTCStats> statsmap = rtcStatsReport.getStatsMap();
                        for(RTCStats rtcStats : statsmap.values()) {
                            if (rtcStats.getType().equals("candidate-pair")) {
                                Map<String, Object> members = rtcStats.getMembers();
                                String state = (String)members.get("state");
                                if(state != null && state.equals("succeeded")) {
                                    BigInteger bytesSent = (BigInteger) members.get("bytesSent");
                                    BigInteger bytesReceived = (BigInteger) members.get("bytesReceived");
                                    if(bytesSent != null && bytesReceived != null) {
                                        BigInteger bytesSentDiff = bytesSent.subtract(WebrtcActivity.this.bytesSent);
                                        BigInteger bytesReceivedDiff = bytesReceived.subtract(WebrtcActivity.this.bytesReceived);
                                        long updateDelay = ChronoUnit.MILLIS.between(lastBandwidthUpdate, LocalDateTime.now());
                                        //dividing bytes by milliseconds is the same as dividing kilobytes by seconds
                                        BigInteger uploadRate = bytesSentDiff.divide(BigInteger.valueOf(updateDelay));
                                        BigInteger downloadRate = bytesReceivedDiff.divide(BigInteger.valueOf(updateDelay));

                                        WebrtcActivity.this.bytesSent = bytesSent;
                                        WebrtcActivity.this.bytesReceived = bytesReceived;
                                        lastBandwidthUpdate = LocalDateTime.now();

                                        Log.i(TAG, "Upload rate: " + uploadRate + "kbps, Downoad rate: " + downloadRate + " kbps");
                                        runOnUiThread(new Runnable() {
                                            @Override
                                            public void run() {
                                                binding.bandwidth.setText(getString(R.string.bandwidth, downloadRate, uploadRate));
                                            }
                                        });
                                    }
                                }
                            }
                        }
                    }
                });
            }
        });
    }

    private void initializePeerConnectionFactory() {
        //PeerConnectionFactory.initializeAndroidGlobals(this, true, true, true);
        final VideoEncoderFactory encoderFactory;
        final VideoDecoderFactory decoderFactory;

        encoderFactory = new DefaultVideoEncoderFactory(rootEglBase.getEglBaseContext(), false /* enableIntelVp8Encoder */, true);
        decoderFactory = new DefaultVideoDecoderFactory(rootEglBase.getEglBaseContext());

        PeerConnectionFactory.initialize(PeerConnectionFactory.InitializationOptions.builder(this)
                .setEnableInternalTracer(true)
                .createInitializationOptions());

        PeerConnectionFactory.Builder builder = PeerConnectionFactory.builder()
                .setVideoEncoderFactory(encoderFactory)
                .setVideoDecoderFactory(decoderFactory);
        builder.setOptions(null);

        factory = builder.createPeerConnectionFactory();
        Log.i(TAG, "Initialized Peer Connection Factory");
    }

    private void createVideoTrackFromCameraAndShowIt() {
        VideoCapturer videoCapturer = createVideoCapturer();

        SurfaceTextureHelper surfaceTextureHelper = SurfaceTextureHelper.create("CaptureThread", rootEglBase.getEglBaseContext());
        VideoSource videoSource = factory.createVideoSource(false);
        videoCapturer.initialize(surfaceTextureHelper, this, new SimpleCapturerObserver(videoSource.getCapturerObserver()));

        videoCapturer.startCapture(VIDEO_RESOLUTION_WIDTH, VIDEO_RESOLUTION_HEIGHT, FPS);

        videoTrackFromCamera = factory.createVideoTrack(VIDEO_TRACK_ID, videoSource);
        videoTrackFromCamera.setEnabled(true);
        Log.i(TAG, "Created camera track");
    }


    private VideoCapturer createVideoCapturer() {
        VideoCapturer videoCapturer;
        if (useCamera2()) {
            videoCapturer = createCameraCapturer(new Camera2Enumerator(this));
        } else {
            videoCapturer = createCameraCapturer(new Camera1Enumerator(true));
        }
        return videoCapturer;
    }

    private VideoCapturer createCameraCapturer(CameraEnumerator enumerator) {
        final String[] deviceNames = enumerator.getDeviceNames();

        // First, try to find front facing camera
        for (String deviceName : deviceNames) {
            if (enumerator.isBackFacing(deviceName)) {
                VideoCapturer videoCapturer = enumerator.createCapturer(deviceName, null);

                if (videoCapturer != null) {
                    Log.i(TAG, "Found Camera Capturer");
                    return videoCapturer;
                }
            }
        }

        // Front facing camera not found, try something else
        for (String deviceName : deviceNames) {
            if (!enumerator.isBackFacing(deviceName)) {
                VideoCapturer videoCapturer = enumerator.createCapturer(deviceName, null);

                if (videoCapturer != null) {
                    Log.i(TAG, "Found Camera Capturer");
                    return videoCapturer;
                }
            }
        }

        Log.e(TAG, "Found NO Camera Capturer");
        return null;
    }

    /*
     * Read more about Camera2 here
     * https://developer.android.com/reference/android/hardware/camera2/package-summary.html
     * */
    private boolean useCamera2() {
        return Camera2Enumerator.isSupported(this);
    }

    private void initializePeerConnections() {
        localPeerConnection = createPeerConnection(factory);
        localPeerConnection.setBitrate(1000000,2000000,10000000);
    }

    private PeerConnection createPeerConnection(PeerConnectionFactory factory) {
        ArrayList<PeerConnection.IceServer> iceServers = new ArrayList<>();
        String URL = "stun:stun.l.google.com:19302";
        String URL2 = "stun:stun.stochastix.de:3478";
        String URL3 = "stun:stun.zentauron.de:3478";
        String URL4 = "stun:stun.studio-link.de:3478";
        String URL5 = "stun:stun.wtfismyip.com:3478";
        String URL6 = "stun:stun.voipconnect.com:3478";
        iceServers.add(new PeerConnection.IceServer(URL));

        PeerConnection.RTCConfiguration rtcConfig = new PeerConnection.RTCConfiguration(iceServers);
        //rtcConfig.bundlePolicy = PeerConnection.BundlePolicy.MAXBUNDLE;
        //rtcConfig.rtcpMuxPolicy = PeerConnection.RtcpMuxPolicy.REQUIRE;
        //rtcConfig.continualGatheringPolicy = PeerConnection.ContinualGatheringPolicy.GATHER_CONTINUALLY;
        rtcConfig.keyType = PeerConnection.KeyType.ECDSA;

        PeerConnection.Observer pcObserver = new SimplePeerConnectionObserver(TAG, binding, this::onIceGatheringComplete);

        localPeerConnection = factory.createPeerConnection(rtcConfig, pcObserver);
        return localPeerConnection;
    }

    private void startStreamingVideo() {
        localPeerConnection.addTrack(videoTrackFromCamera);

        MediaConstraints sdpMediaConstraints = new MediaConstraints();

        localPeerConnection.createOffer(new SimpleSdpObserver() {
            @Override
            public void onCreateSuccess(SessionDescription sdp) {
                localPeerConnection.setLocalDescription(new SimpleSdpObserver() {
                    @Override
                    public void onSetSuccess() {
                        Log.i(TAG, "onCreateSuccess: SDP Offer: " + localPeerConnection.getLocalDescription().type + " \n" + localPeerConnection.getLocalDescription().description);
                    }
                }, sdp);
            }
        }, sdpMediaConstraints);
    }

    public void onIceGatheringComplete() {
        Log.i(TAG, "onIceGatheringComplete: SDP Offer: " + localPeerConnection.getLocalDescription().type + " \n" + localPeerConnection.getLocalDescription().description);

        sendOfferSdp(localPeerConnection.getLocalDescription());
    }

    public void sendOfferSdp(SessionDescription sdp) {
        OfferService offerService = new OfferService(
                this,
                this::onOfferSuccess,
                this::onOfferFailure,
                this::onRequestFailure
        );

        offerService.offer(new Offer(sdp.description, "offer", "tsdr"));
    }

    private void onOfferSuccess(Response<Offer> response) {
        Toast.makeText(this, "Sending Offer successful", Toast.LENGTH_SHORT).show();
        SessionDescription.Type type = SessionDescription.Type.valueOf(response.body().getType().toUpperCase());
        SessionDescription answer = new SessionDescription(type, response.body().getSdp());
        localPeerConnection.setRemoteDescription(new SimpleSdpObserver() {
            @Override
            public void onSetSuccess() {
                Log.i(TAG, "onSetSuccess: SDP Answer: " + localPeerConnection.getRemoteDescription().type + " \n" + localPeerConnection.getRemoteDescription().description);

                //RtpSender sender = localPeerConnection.getSenders().get(0);
                //RtpParameters parameters = sender.getParameters();
                //parameters.encodings.get(0).maxBitrateBps = 10 * 1000 * 1000;
                //sender.setParameters(parameters);
            }
        }, answer);
    }

    private void onOfferFailure(Response<Offer> response) {
        Toast.makeText(this, "Sending Offer failed", Toast.LENGTH_SHORT).show();
    }

    private void onRequestFailure(Throwable t) {
        Toast.makeText(this, "Request failed. Bad connection?", Toast.LENGTH_SHORT).show();
    }

}
