package com.example.frontend.activity;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

import com.example.frontend.R;
import com.example.frontend.schema.UserSchema;
import com.example.frontend.service.LoginService;
import com.google.android.material.button.MaterialButton;

public class MainActivity extends AppCompatActivity {
    private static final String[] CAMERA_PERMISSION = new String[]{Manifest.permission.CAMERA};
    private static final int CAMERA_REQUEST_CODE = 10;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // get layout elements
        MaterialButton loginbtn = findViewById(R.id.loginbtn);
        EditText username = findViewById(R.id.username);
        EditText password = findViewById(R.id.password);

        // define login service with lambdas handling login success and login failure
        LoginService loginService = new LoginService(this, this::enableCamera, this::showLoginError);

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

    private void showLoginError() {
        findViewById(R.id.notification).setVisibility(View.VISIBLE);
    }

    private void enableCamera() {
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
                enableCamera();
            } else {
                Log.i(this.getClass().getName(), "Camera permissions denied");
                Toast.makeText(this, "Camera permission denied", Toast.LENGTH_SHORT).show();
                finishAndRemoveTask();
            }
        }
    }
}