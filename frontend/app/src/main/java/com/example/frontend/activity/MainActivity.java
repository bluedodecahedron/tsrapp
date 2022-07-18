package com.example.frontend.activity;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.camera.core.ExperimentalGetImage;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.example.frontend.R;
import com.example.frontend.schema.UserSchema;
import com.example.frontend.service.LoginService;
import com.google.android.material.button.MaterialButton;

import okhttp3.ResponseBody;
import retrofit2.Response;

@ExperimentalGetImage
public class MainActivity extends AppCompatActivity {
    private static final String[] CAMERA_PERMISSION = new String[]{Manifest.permission.CAMERA};
    private static final int CAMERA_REQUEST_CODE = 10;

    private LoginService loginService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // get layout elements
        MaterialButton loginbtn = findViewById(R.id.loginbtn);
        EditText username = findViewById(R.id.username);
        EditText password = findViewById(R.id.password);

        // get new login service handling login success and login failure (lambdas)
        loginService = new LoginService(
                this,
                this::onLoginSuccess,
                this::onLoginFailure,
                this::onRequestFailure
        );

        // get remembered user
        UserSchema rememberedUser = loginService.getRememberedUser();
        if(rememberedUser != null) {
            username.setText(rememberedUser.getUsername());
            password.setText(rememberedUser.getPassword());
        }

        // define login button click
        loginbtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                UserSchema user = new UserSchema(username.getText().toString(), password.getText().toString());
                loginService.login(user);
            }
        });

    }

    private void onLoginSuccess(Response<ResponseBody> response) {
        Toast.makeText(this, "Login successful", Toast.LENGTH_SHORT).show();
        //enableTsdrHttp();
        enableTsdrWebRTC();
    }

    private void onLoginFailure(Response<ResponseBody> response) {
        findViewById(R.id.notification).setVisibility(View.VISIBLE);
    }

    private void onRequestFailure(Throwable t) {
        Toast.makeText(this, "Request failed. Bad connection?", Toast.LENGTH_SHORT).show();
    }

    private void enableTsdrWebRTC() {
        Intent intent = new Intent(this, WebRTCActivity.class);
        startActivity(intent);
    }

    private void enableTsdrHttp() {
        if (hasCameraPermission()) {
            Intent intent = new Intent(this, CameraActivity.class);
            startActivity(intent);
        } else {
            requestPermission();
        }
    }

    private boolean hasCameraPermission() {
        return ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.CAMERA
        ) == PackageManager.PERMISSION_GRANTED;
    }

    private void requestPermission() {
        ActivityCompat.requestPermissions(
                this,
                CAMERA_PERMISSION,
                CAMERA_REQUEST_CODE
        );
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == CAMERA_REQUEST_CODE) {
            if (grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Log.i(this.getClass().getName(), "Camera permissions granted");
                enableTsdrHttp();
            } else {
                Log.i(this.getClass().getName(), "Camera permissions denied");
                Toast.makeText(this, "Camera permission denied", Toast.LENGTH_SHORT).show();
                finishAndRemoveTask();
            }
        }
    }
}