/*
 * Copyright (c) 2017. Noah Gao <noahgaocn@gmail.com>
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

package net.noahgao.freeiot.util;

import android.Manifest;
import android.app.Activity;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AlertDialog;
import android.widget.Toast;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;

import net.noahgao.freeiot.BuildConfig;
import net.noahgao.freeiot.MainApplication;
import net.noahgao.freeiot.service.UpdateService;

import im.fir.sdk.FIR;
import im.fir.sdk.VersionCheckCallback;

public class UpdateManager {

    static public void doUpdate(Activity context) {
        doUpdate(context, true);
    }

    static public void doUpdate(final Activity context, final boolean noupdateToast) {
        FIR.checkForUpdateInFIR(BuildConfig.FIR_API_TOKEN, new VersionCheckCallback() {
            @Override
            public void onSuccess(String versionJson) {
                final JSONObject version = JSON.parseObject(versionJson);
                if (Float.parseFloat(MainApplication.versionName) < Float.parseFloat((String) version.get("versionShort")) || (Float.parseFloat(MainApplication.versionName) == Float.parseFloat(version.getString("versionShort")) && MainApplication.versionCode < Integer.parseInt(version.getString("build")))) {
                    new AlertDialog.Builder(context)
                            .setTitle("有更新！")
                            .setMessage("版本号:" + version.getString("versionShort") + "." + version.getString("build") + "\n日志:" + version.getString("changelog"))
                            .setPositiveButton(
                                    "确定",
                                    new DialogInterface.OnClickListener() {
                                        @Override
                                        public void onClick(DialogInterface dialog, int which) {
                                            if (ActivityCompat.checkSelfPermission(context, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                                                Toast.makeText(context,"更新权限不足！",Toast.LENGTH_SHORT).show();
                                                return;
                                            }
                                            Intent updataService = new Intent(context,  UpdateService.class);
                                            updataService.putExtra("downloadurl",version.getString("installUrl"));
                                            context.startService(updataService);
                                        }
                                    })
                            .setNegativeButton(
                                    "取消", null).show();

                } else {
                    if(noupdateToast) Toast.makeText(context,"当前版本已是最新！", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFail(Exception exception) {
                //
                Toast.makeText(context,"更新信息抓取失败！ " + "\n" + exception.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }
}