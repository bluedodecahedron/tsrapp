package com.example.frontend.service.client;

import com.example.frontend.schema.UserSchema;

import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.POST;

public interface API {
    @POST("api/authentication/login")
    Call<ResponseBody> login(@Body UserSchema userSchema);

    @POST("api/tsdr/test")
    Call<ResponseBody> test();
}