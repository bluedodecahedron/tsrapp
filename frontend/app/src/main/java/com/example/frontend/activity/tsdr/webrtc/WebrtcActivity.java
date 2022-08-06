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
import com.example.frontend.activity.tsdr.webrtc.observers.CustomCapturerObserver;
import com.example.frontend.activity.tsdr.webrtc.observers.CustomPeerConnectionObserver;
import com.example.frontend.activity.tsdr.webrtc.observers.CustomSdpObserver;
import com.example.frontend.activity.tsdr.webrtc.video.StatisticsRenderer;
import com.example.frontend.activity.tsdr.webrtc.video.VideoCapturerFactory;
import com.example.frontend.databinding.ActivityWebrtcBinding;
import com.example.frontend.schema.Offer;
import com.example.frontend.service.OfferService;

import org.webrtc.DefaultVideoDecoderFactory;
import org.webrtc.DefaultVideoEncoderFactory;
import org.webrtc.EglBase;
import org.webrtc.MediaConstraints;
import org.webrtc.PeerConnection;
import org.webrtc.PeerConnectionFactory;
import org.webrtc.RendererCommon;
import org.webrtc.SessionDescription;
import org.webrtc.SurfaceTextureHelper;
import org.webrtc.VideoCapturer;
import org.webrtc.VideoDecoderFactory;
import org.webrtc.VideoEncoderFactory;
import org.webrtc.VideoSource;
import org.webrtc.VideoTrack;

import java.util.ArrayList;

import pub.devrel.easypermissions.AfterPermissionGranted;
import pub.devrel.easypermissions.EasyPermissions;
import retrofit2.Response;

public class WebrtcActivity extends AppCompatActivity {
    private static final String TAG = WebrtcActivity.class.getSimpleName();
    private static final int RC_CALL = 120;
    public static final String VIDEO_TRACK_ID = "ARDAMSv0";
    public static final int VIDEO_RESOLUTION_WIDTH = 800; // Video capturer chooses the next closest supported resolution for the device
    public static final int VIDEO_RESOLUTION_HEIGHT = 500;
    public static final int FPS = 15; // Video capturer chooses the next closest supported fps value for the device

    private ActivityWebrtcBinding binding;
    private PeerConnection localPeerConnection;
    private EglBase rootEglBase;
    private PeerConnectionFactory factory;
    private SurfaceTextureHelper surfaceTextureHelper;
    private VideoCapturer videoCapturer;
    private VideoTrack videoTrackFromCamera;

    private StatisticsRenderer statsRenderer;

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
            //initialize video renderer
            initializeSurfaceRenderer();

            //initialize factory used to create peer connections and create video tracks
            initializePeerConnectionFactory();

            //create video track from device camera (constantly produces camera video footage)
            createVideoTrackFromCamera();

            //initialize peer connection
            initializePeerConnection();

            //send offer, receive counter-offer, send camera video footage, receive analyzed video
            sendOfferAndSendVideo();
        } else {
            Log.i(TAG, "Requesting Permissions");
            EasyPermissions.requestPermissions(this, "Need some permissions", RC_CALL, perms);
        }
    }

    private void initializeSurfaceRenderer() {
        rootEglBase = EglBase.create();

        binding.surfaceRenderer.init(rootEglBase.getEglBaseContext(), null);
        binding.surfaceRenderer.setScalingType(RendererCommon.ScalingType.SCALE_ASPECT_FILL); //NEW
        binding.surfaceRenderer.setEnableHardwareScaler(true);
        binding.surfaceRenderer.setMirror(false);
        binding.surfaceRenderer.setTAG(TAG);

        Log.i(TAG, "Initialized surface views");
    }

    private void initializePeerConnectionFactory() {
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

    private void createVideoTrackFromCamera() {
        VideoCapturerFactory videoCapturerFactory = new VideoCapturerFactory(TAG, this);
        videoCapturer = videoCapturerFactory.createVideoCapturer();

        surfaceTextureHelper = SurfaceTextureHelper.create("CaptureThread", rootEglBase.getEglBaseContext());
        VideoSource videoSource = factory.createVideoSource(false);
        videoCapturer.initialize(surfaceTextureHelper, this, new CustomCapturerObserver(videoSource.getCapturerObserver()));

        videoCapturer.startCapture(VIDEO_RESOLUTION_WIDTH, VIDEO_RESOLUTION_HEIGHT, FPS);

        videoTrackFromCamera = factory.createVideoTrack(VIDEO_TRACK_ID, videoSource);
        videoTrackFromCamera.setEnabled(true);
        Log.i(TAG, "Created camera track");
    }

    private void initializePeerConnection() {
        localPeerConnection = createPeerConnection(factory);
        localPeerConnection.setBitrate(500000,2000000,4000000);
        statsRenderer = new StatisticsRenderer(this, binding, localPeerConnection, TAG);
        binding.surfaceRenderer.setStatsRenderer(statsRenderer);
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
        //rtcConfig.allowCodecSwitching = false;
        //rtcConfig.continualGatheringPolicy = PeerConnection.ContinualGatheringPolicy.GATHER_CONTINUALLY;
        //rtcConfig.keyType = PeerConnection.KeyType.ECDSA;
        //rtcConfig.suspendBelowMinBitrate = false;
        //rtcConfig.networkPreference = PeerConnection.AdapterType.WIFI;
        //rtcConfig.candidateNetworkPolicy = PeerConnection.CandidateNetworkPolicy.LOW_COST;

        PeerConnection.Observer pcObserver = new CustomPeerConnectionObserver(TAG, binding, this::onIceGatheringComplete);

        localPeerConnection = factory.createPeerConnection(rtcConfig, pcObserver);
        return localPeerConnection;
    }

    private void sendOfferAndSendVideo() {
        localPeerConnection.addTrack(videoTrackFromCamera);

        MediaConstraints sdpMediaConstraints = new MediaConstraints();

        localPeerConnection.createOffer(new CustomSdpObserver() {
            @Override
            public void onCreateSuccess(SessionDescription sdp) {
                localPeerConnection.setLocalDescription(new CustomSdpObserver() {
                    @Override
                    public void onSetSuccess() {
                        //After successful setting of local description, ice candidates are gathered
                        //When ice gathering is complete, the function onIceGatheringComplete is triggered
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
        localPeerConnection.setRemoteDescription(new CustomSdpObserver() {
            @Override
            public void onSetSuccess() {
                //After successful setting of remote description, video sending begins
                //When analyzed video was received from server, the function onAddTrack in PeerConnectionObserver is triggered
                Log.i(TAG, "onSetSuccess: SDP Answer: " + localPeerConnection.getRemoteDescription().type + " \n" + localPeerConnection.getRemoteDescription().description);

                //RtpSender sender = localPeerConnection.getSenders().get(0);
                //RtpParameters.Encoding encoding = sender.getParameters().encodings.get(0);
            }
        }, answer);
    }

    private void onOfferFailure(Response<Offer> response) {
        Toast.makeText(this, "Sending Offer failed", Toast.LENGTH_SHORT).show();
    }

    private void onRequestFailure(Throwable t) {
        Toast.makeText(this, "Request failed. Bad connection?", Toast.LENGTH_SHORT).show();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        Log.i(TAG, "Destroying WebRTC Activity");
        closeConnection();
        //message.put("userId", RTCSignalClient.getInstance().getUserId());
        //RTCSignalClient.getInstance().sendMessage(message);
        binding.surfaceRenderer.release();
        videoCapturer.dispose();
        surfaceTextureHelper.dispose();
        PeerConnectionFactory.stopInternalTracingCapture();
        PeerConnectionFactory.shutdownInternalTracer();
    }

    private void closeConnection() {
        Log.i(TAG, ("Closing Peer Connection"));
        if (localPeerConnection == null) {
            return;
        }
        localPeerConnection.close();
        localPeerConnection = null;
    }

    @Override
    protected void onResume() {
        super.onResume();
        videoCapturer.startCapture(VIDEO_RESOLUTION_WIDTH, VIDEO_RESOLUTION_HEIGHT, FPS);
    }

    @Override
    protected void onPause() {
        super.onPause();
        try {
            videoCapturer.stopCapture();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
