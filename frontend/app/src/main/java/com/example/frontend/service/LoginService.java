package com.example.frontend.service;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;
import android.util.Log;
import android.widget.Toast;

import com.example.frontend.service.client.API;
import com.example.frontend.service.client.RetrofitClient;
import com.example.frontend.schema.UserSchema;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;

import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class LoginService {
    Context context;
    Runnable onLoginSuccess;
    Runnable onLoginFailure;
    boolean loggedIn;

    public LoginService(Context context, Runnable onLoginSuccess, Runnable onLoginFailure) {
        this.context = context;
        this.onLoginSuccess = onLoginSuccess;
        this.onLoginFailure = onLoginFailure;
    }

    public void login(UserSchema user) {
        cleanCookies();

        List<String> bla = new ArrayList<>();

        //get request call
        API api = RetrofitClient.getInstance(context).getAPI();
        Call<ResponseBody> call = api.login(user);

        //queue request (is handled asynchronously)
        LoginCallback callback = new LoginCallback(user);
        call.enqueue(callback);
    }

    private void cleanCookies() {
        HashSet<String> cookies = new HashSet<>();
        SharedPreferences.Editor memes = PreferenceManager.getDefaultSharedPreferences(context).edit();
        memes.putStringSet("PREF_COOKIES", cookies).apply();
        memes.commit();
    }

    class LoginCallback implements Callback<ResponseBody> {
        UserSchema user;

        public LoginCallback(UserSchema user) {
            super();
            this.user = user;
        }

        @Override
        public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
            if(response.isSuccessful()) {
                handleLoginSuccess(user, response);
                onLoginSuccess.run();
            } else {
                handleLoginFailure(user, response);
                onLoginFailure.run();
            }
        }

        @Override
        public void onFailure(Call<ResponseBody> call, Throwable t) {
            handleRequestFailure(user, t);
        }
    }

    private void handleLoginSuccess(UserSchema user, Response<ResponseBody> response) {
        loggedIn = true;

        //success message
        Log.i(this.getClass().getName(), "LOGIN SUCCESSFUL");
        Log.i(this.getClass().getName(), "API TIME: " + getApiTime(response) + "ms");
        Toast.makeText(context, "Login successful", Toast.LENGTH_SHORT).show();

        rememberUser(user.getUsername(), user.getPassword());
    }

    private void handleLoginFailure(UserSchema user, Response<ResponseBody> response) {
        loggedIn = false;

        //error message
        Log.e(this.getClass().getName(), "Login request failed with status code " + response.code() + ": " + response.message());
    }

    private void handleRequestFailure(UserSchema user, Throwable t) {
        Toast.makeText(context, "Login Request failed", Toast.LENGTH_SHORT).show();
        t.printStackTrace();
    }

    private long getApiTime(Response<ResponseBody> response) {
        long requestTime = response.raw().sentRequestAtMillis();
        // time when the response was received
        long responseTime = response.raw().receivedResponseAtMillis();
        //time taken to receive the response after the request was sent
        return  responseTime - requestTime;
    }

    private void rememberUser(String username, String password) {
        SharedPreferences sp=context.getSharedPreferences("Login", Context.MODE_PRIVATE);
        SharedPreferences.Editor Ed=sp.edit();
        Ed.putString("username",username );
        Ed.putString("password",password);
        Ed.commit();
    }

    public UserSchema getRememberedUser() {
        SharedPreferences sp1=context.getSharedPreferences("Login", Context.MODE_PRIVATE);

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
}
