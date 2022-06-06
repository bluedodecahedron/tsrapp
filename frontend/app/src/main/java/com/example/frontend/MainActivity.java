package com.example.frontend;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.Manifest;
import android.accounts.AbstractAccountAuthenticator;
import android.accounts.Account;
import android.accounts.AccountAuthenticatorResponse;
import android.accounts.AccountManager;
import android.accounts.NetworkErrorException;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.google.android.material.button.MaterialButton;

public class MainActivity extends AppCompatActivity {
    private static final String[] CAMERA_PERMISSION = new String[]{Manifest.permission.CAMERA};
    private static final int CAMERA_REQUEST_CODE = 10;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        UserSchema rememberedUser = getRememberedUser();

        MaterialButton loginbtn = (MaterialButton) findViewById(R.id.loginbtn);
        EditText username = (EditText)findViewById(R.id.username);
        EditText password = (EditText)findViewById(R.id.password);

        if(rememberedUser != null) {
            username.setText(rememberedUser.getUsername());
            password.setText(rememberedUser.getPassword());
        }

        loginbtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                login(username, password);
            }
        });

    }

    public void login(EditText username, EditText password) {
        if (username.getText().toString().equals("admin") && password.getText().toString().equals("admin")) {
            Toast.makeText(this, "Login successful", Toast.LENGTH_SHORT).show();
            Log.i(this.getClass().getName(), "Login successful");
            rememberUser(username.getText().toString(), password.getText().toString());
            enableCamera();
        } else {
            findViewById(R.id.notification).setVisibility(View.VISIBLE);
            Log.i(this.getClass().getName(), "Login failed");
        }
    }

    private void rememberUser(String username, String password) {
        SharedPreferences sp=getSharedPreferences("Login", MODE_PRIVATE);
        SharedPreferences.Editor Ed=sp.edit();
        Ed.putString("username",username );
        Ed.putString("password",password);
        Ed.commit();
    }

    private UserSchema getRememberedUser() {
        SharedPreferences sp1=this.getSharedPreferences("Login", MODE_PRIVATE);

        if (sp1.contains("username") && sp1.contains("password")) {
            String username=sp1.getString("username", null);
            String password = sp1.getString("password", null);

            Log.i(this.getClass().getName(), "Retrieved remembered user: "  + username );
            return new UserSchema(username, password);
        } else {
            Log.i(this.getClass().getName(), "No remembered user");
            return null;
        }
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