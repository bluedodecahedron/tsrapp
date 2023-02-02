package com.example.frontend.activity.tsdr.webrtc;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import androidx.appcompat.app.AppCompatActivity;
import androidx.databinding.DataBindingUtil;
import com.example.frontend.databinding.ActivityStoppedBinding;

import com.example.frontend.R;
import com.example.frontend.schema.User;

public class StoppedActivity extends AppCompatActivity {
    private static final String TAG = StoppedActivity.class.getSimpleName();

    private ActivityStoppedBinding binding;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = DataBindingUtil.setContentView(this, R.layout.activity_stopped);

        binding.startbtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startTsdrWebRTC();
            }
        });
    }

    private void startTsdrWebRTC() {
        Intent intent = new Intent(this, WebrtcActivity.class);
        startActivity(intent);
    }
}
