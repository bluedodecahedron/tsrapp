package com.example.frontend.service;

import android.content.Context;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;
import android.util.Log;

import com.example.frontend.schema.User;
import com.example.frontend.service.HttpClient.API;
import com.example.frontend.service.HttpClient.RetrofitClient;
import com.example.frontend.util.NetworkMeasures;

import java.util.HashSet;
import java.util.function.Consumer;

import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class LoginService {
    Context context;
    Consumer<Response<ResponseBody>> onLoginSuccess;
    Consumer<Response<ResponseBody>> onLoginFailure;
    Consumer<Throwable> onRequestFailure;

    public LoginService(
            Context context,
            Consumer<Response<ResponseBody>> onLoginSuccess,
            Consumer<Response<ResponseBody>> onLoginFailure,
            Consumer<Throwable> onRequestFailure
    ) {
        this.context = context;
        this.onLoginSuccess = onLoginSuccess;
        this.onLoginFailure = onLoginFailure;
        this.onRequestFailure = onRequestFailure;
    }

    public void login(User user) {
        cleanCookies();

        //get request call
        API api = RetrofitClient.getInstance(context).getAPI();
        Call<ResponseBody> call = api.login(user);

        //queue request (is handled asynchronously)
        call.enqueue(new LoginCallback(user));
    }

    private void cleanCookies() {
        HashSet<String> cookies = new HashSet<>();
        SharedPreferences.Editor memes = PreferenceManager.getDefaultSharedPreferences(context).edit();
        memes.putStringSet("PREF_COOKIES", cookies).apply();
        memes.commit();
    }

    class LoginCallback implements Callback<ResponseBody> {
        User user;

        public LoginCallback(User user) {
            super();
            this.user = user;
        }

        @Override
        public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
            if(response.isSuccessful()) {
                handleLoginSuccess(user, response);
                onLoginSuccess.accept(response);
            } else {
                handleLoginFailure(user, response);
                onLoginFailure.accept(response);
            }
        }

        @Override
        public void onFailure(Call<ResponseBody> call, Throwable t) {
            handleRequestFailure(t);
            onRequestFailure.accept(t);
        }
    }

    private void handleLoginSuccess(User user, Response<ResponseBody> response) {
        Log.i(this.getClass().getName(), "Login successful, response time: " + NetworkMeasures.getResponseTime(response) + "ms");
        rememberUser(user.getUsername(), user.getPassword());
    }

    private void handleLoginFailure(User user, Response<ResponseBody> response) {
        Log.e(this.getClass().getName(), "Login request for " + user.getUsername() + " failed with status code " + response.code() + ": " + response.message());
    }

    private void handleRequestFailure(Throwable t) {
        Log.e(this.getClass().getName(), "Request failed. Bad connection?");
        t.printStackTrace();
    }

    private void rememberUser(String username, String password) {
        SharedPreferences sp=context.getSharedPreferences("Login", Context.MODE_PRIVATE);
        SharedPreferences.Editor Ed=sp.edit();
        Ed.putString("username",username );
        Ed.putString("password",password);
        Ed.commit();
    }

    public User getRememberedUser() {
        SharedPreferences sp1=context.getSharedPreferences("Login", Context.MODE_PRIVATE);

        if (sp1.contains("username") && sp1.contains("password")) {
            String username=sp1.getString("username", null);
            String password = sp1.getString("password", null);

            Log.i(this.getClass().getName(), "Retrieved remembered user: "  + username );
            return new User(username, password);
        } else {
            Log.i(this.getClass().getName(), "No remembered user");
            return null;
        }
    }
}
