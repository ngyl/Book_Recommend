<template>
    <div class="register-container">
        <h1 style="cursor: pointer;">欢迎注册</h1>
        <el-form :model="UserForm" label-with="auto" :rules="rules" class="register-form">
            <el-form-item label="账号" prop="id">
                <el-input v-model="UserForm.id" placeholder="账号"/>
            </el-form-item> 
            <el-form-item label="密码" prop="password">
                <el-input v-model="UserForm.password" placeholder="密码" type="password" show-password/>
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
                <el-input v-model="UserForm.confirmPassword" placeholder="确认密码" type="password" show-password/>
            </el-form-item>
            <div class="button-container">
                <el-button type="primary" size="default" round plain @click="register">注册</el-button>
            </div>
        </el-form>
    </div>
</template>

<script setup lang="ts">
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { reactive } from 'vue';
import router from '../router';


const UserForm = reactive({
    id: '',
    password: '',
    confirmPassword: '',
});

const rules = reactive({
  id: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: (_rule: any, value: string, callback: (error?: Error) => void) => {
      if (value !== UserForm.password) {
        callback(new Error('两次输入的密码不一致'));
      } else {
        callback();
      }
    }, trigger: 'blur' }
  ],
});

const register = async () => {
  if (UserForm.id === '' || UserForm.password === '' || UserForm.confirmPassword === '') {
    ElMessage({
      message: '请完整填写所有字段',
      type: 'error',
      duration: 1000,
    });
    return;
  }

  try {
    const response = await axios({
      method: 'post',
      url: 'http://localhost:5000/api/register',
      data: {
        id: UserForm.id,
        password: UserForm.password,
      },
    });

    if (response.status === 200) {
      ElMessage({
        message: '注册成功',
        type: 'success',
        duration: 1000,
      });

      router.push('/login');
    } else {
      ElMessage({
        message: response.data.message || '注册失败',
        type: 'error',
        duration: 1000,
      });
    }
  } catch (error) {
    ElMessage({
      message: '注册请求失败',
      type: 'error',
      duration: 1000,
    });
    console.log(error);
  }
};

</script>

<style scoped>
.register-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 100%;
    overflow: hidden;
    box-sizing: border-box;
    transform: translateY(-80px);
}

.el-from-item {
    width: 100%;
}

.el-input {
    width: 100%
}

.register-form {
    width:300px
}

.button-container {
    display: flex;
    justify-content: center;
}

</style>

<!-- <style>
html, body {
    height: 100%;
    margin: 0;
    padding: 0;
    overflow: hidden;
}
</style> -->