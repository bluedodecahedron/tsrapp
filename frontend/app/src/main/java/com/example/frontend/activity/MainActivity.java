package com.example.frontend.activity;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.StringRes;
import androidx.appcompat.app.AppCompatActivity;
import androidx.camera.core.ExperimentalGetImage;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.example.frontend.R;
import com.example.frontend.activity.tsdr.http.HttpActivity;
import com.example.frontend.activity.tsdr.webrtc.StoppedActivity;
import com.example.frontend.activity.tsdr.webrtc.WebrtcActivity;
import com.example.frontend.schema.User;
import com.example.frontend.service.LoginService;
import com.google.android.material.button.MaterialButton;

import java.util.List;

import okhttp3.ResponseBody;
import pub.devrel.easypermissions.AfterPermissionGranted;
import pub.devrel.easypermissions.AppSettingsDialog;
import pub.devrel.easypermissions.EasyPermissions;
import retrofit2.Response;

@ExperimentalGetImage
public class MainActivity extends AppCompatActivity implements EasyPermissions.PermissionCallbacks {
    private static final String TAG = MainActivity.class.getSimpleName();
    private static final String[] CAMERA_PERMISSION = new String[]{Manifest.permission.CAMERA};
    private static final int CAMERA_REQUEST_CODE = 10;
    private static final int RC_CALL = 120;

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
        User rememberedUser = loginService.getRememberedUser();
        if(rememberedUser != null) {
            username.setText(rememberedUser.getUsername());
            password.setText(rememberedUser.getPassword());
        }

        // define login button click
        loginbtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                User user = new User(username.getText().toString(), password.getText().toString());
                loginService.login(user);
            }
        });

    }

    private void onLoginSuccess(Response<ResponseBody> response) {
        Toast.makeText(this, "Login successful", Toast.LENGTH_SHORT).show();
        startTsdr();
    }

    private void onLoginFailure(Response<ResponseBody> response) {
        findViewById(R.id.notification).setVisibility(View.VISIBLE);
    }

    private void onRequestFailure(Throwable t) {
        Toast.makeText(this, "Request failed. Bad connection?", Toast.LENGTH_SHORT).show();
    }

    @AfterPermissionGranted(RC_CALL)
    private void startTsdr() {
        String[] perms = {Manifest.permission.CAMERA};
        Log.i(TAG, "Checking Permissions");
        if (EasyPermissions.hasPermissions(this, perms)) {
            //startTsdrHttp();
            startTsdrWebRTC();
        } else {
            Log.i(TAG, "Requesting Permissions");
            EasyPermissions.requestPermissions(this, "Need some permissions", RC_CALL, perms);
        }
    }

    private void startTsdrWebRTC() {
        Intent intent = new Intent(this, StoppedActivity.class);
        startActivity(intent);
    }

    private void startTsdrHttp() {
        Intent intent = new Intent(this, HttpActivity.class);
        startActivity(intent);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        EasyPermissions.onRequestPermissionsResult(requestCode, permissions, grantResults, this);
    }

    @Override
    public void onPermissionsGranted(int requestCode, @NonNull List<String> perms) {
        Log.i(this.getClass().getName(), "Camera permissions granted");
    }

    @Override
    public void onPermissionsDenied(int requestCode, @NonNull List<String> perms) {
        Log.i(this.getClass().getName(), "Camera permissions denied");
        TextView notification = findViewById(R.id.notification);
        notification.setText(this.getResources().getString(R.string.perm_denied));
        notification.setVisibility(View.VISIBLE);
        // (Optional) Check whether the user denied any permissions and checked "NEVER ASK AGAIN."
        // This will display a dialog directing them to enable the permission in app settings.
        if (EasyPermissions.somePermissionPermanentlyDenied(this, perms)) {
            new AppSettingsDialog.Builder(this).build().show();
        }
    }
}