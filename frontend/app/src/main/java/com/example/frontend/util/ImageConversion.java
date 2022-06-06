package com.example.frontend.util;

import android.content.Context;
import android.content.ContextWrapper;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.ImageFormat;
import android.graphics.Rect;
import android.graphics.YuvImage;
import android.media.Image;
import android.util.Log;

import androidx.camera.core.ExperimentalGetImage;
import androidx.camera.core.ImageProxy;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;

import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.RequestBody;

@ExperimentalGetImage
public class ImageConversion {
    Context context;

    public ImageConversion(Context context) {
        this.context = context;
    }

    public MultipartBody.Part toFormData(ImageProxy imageProxy) {
        // convert image
        Image image = toImage(imageProxy);
        Bitmap bitmap = toBitmap(image);
        File imageFile = toFile(bitmap);
        MultipartBody.Part formData = toFormData(imageFile);

        return formData;
    }

    private Image toImage(ImageProxy imageProxy) {
        return imageProxy.getImage();
    }

    // source: https://gist.github.com/Ahwar/b6797f81671b2f8fb3f7cc5de3c9a5dc
    private Bitmap toBitmap(Image image) {
        Image.Plane[] planes = image.getPlanes();
        ByteBuffer yBuffer = planes[0].getBuffer();
        ByteBuffer uBuffer = planes[1].getBuffer();
        ByteBuffer vBuffer = planes[2].getBuffer();

        int ySize = yBuffer.remaining();
        int uSize = uBuffer.remaining();
        int vSize = vBuffer.remaining();

        byte[] nv21 = new byte[ySize + uSize + vSize];
        //U and V are swapped
        yBuffer.get(nv21, 0, ySize);
        vBuffer.get(nv21, ySize, vSize);
        uBuffer.get(nv21, ySize + vSize, uSize);

        YuvImage yuvImage = new YuvImage(nv21, ImageFormat.NV21, image.getWidth(), image.getHeight(), null);
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        yuvImage.compressToJpeg(new Rect(0, 0, yuvImage.getWidth(), yuvImage.getHeight()), 75, out);

        byte[] imageBytes = out.toByteArray();
        return BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.length);
    }

    private File toFile(Bitmap bitmap) {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        if(!bitmap.compress(Bitmap.CompressFormat.JPEG, 90, bytes)) {
            throw new RuntimeException("Compression of image failed. Couldn't save file.");
        }

        ContextWrapper cw = new ContextWrapper(context);
        // path to /data/data/myapp/app_data/imageDir
        File directory = context.getDir("imageDir", Context.MODE_PRIVATE);
        File destination = new File(directory, "tmpImage.jpg");

        try (FileOutputStream fo = new FileOutputStream(destination)) {
            fo.write(bytes.toByteArray());
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        File file =  new File(destination.getAbsolutePath());
        Log.i(this.getClass().getName(), "Successful image file load");
        return file;
    }

    private MultipartBody.Part toFormData(File imageFile) {
        RequestBody reqBody = RequestBody.create(MediaType.parse("multipart/form-file"), imageFile);
        MultipartBody.Part partImage = MultipartBody.Part.createFormData("image_file", imageFile.getName(), reqBody);
        Log.i(this.getClass().getName(), "Successful form data creation");
        return partImage;
    }
}
