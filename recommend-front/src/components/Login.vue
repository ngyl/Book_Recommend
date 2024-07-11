<template>
    <div class="login-container">
        <h1 style="cursor: pointer;">图书推荐系统</h1>
        <el-form :model="loginForm" :rules="rules" hide-required-asterisk="true" class="login-form">
          <el-form-item label="账号" prop="id">
            <el-input :prefix-icon="User" v-model="loginForm.id" placeholder="请输入账号"/>
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input :prefix-icon="Lock" v-model="loginForm.password" placeholder="请输入密码" type="password" show-password />
          </el-form-item>
          <div class="button-container">
            <el-button type="primary" size="large" round plain @click="login">登录</el-button>
          </div>
        </el-form>
    </div>
</template>

<script setup lang="ts">
import { Lock, User } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { reactive, defineEmits } from 'vue';
import router from '../router';
import axios from 'axios';

const loginForm = reactive({
    id: "",
    password: "",
})

const rules = reactive({
    id: [{ required: true, message: '请输入账号', trigger: 'blur' }],
    password: [{ required: true, message: '请选择密码', trigger: 'change' }]
})
            
const emit = defineEmits(['LoggedIn'])


const login = async () => {
    if (loginForm.id == "" || loginForm.password == "") {
        ElMessage({
          message: "账号或密码不能为空",
          type: "error",
          duration: 1000
        })

        return;
    }

    try {
        const response = await axios({
            method:'post',
            url: "http://localhost:5000/api/login",
            data: {
                id: loginForm.id,
                password: loginForm.password
            }
        })

        if (response.status === 200) {
            ElMessage({
                message: '登录成功',
                type: 'success',
                duration: 1000,
            });

            // console.log(response.data)
            // console.log(response.data.data)
            // console.log(response.data.data[0])
            // console.log(localStorage.getItem("username"))
            // console.log(localStorage.getItem("id"))

            localStorage.setItem("username", JSON.stringify(response.data.data[0].username))
            localStorage.setItem("id",JSON.stringify(response.data.data[0].id))

            emit('LoggedIn', true, response.data.data[0].username);
            

            router.push('/')
            return
        } else {
            ElMessage({
                message: response.data.message || '登录失败',
                type: 'error',
                duration: 1000.
            });
            return
        }
    } catch (error) {
        ElMessage({
        message: '登录请求失败',
        type: 'error',
        duration: 1000,
        });

        console.log(error)
    }
}

</script>

<style scoped>
.login-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 100%;
    overflow: hidden;
    box-sizing: border-box;
    transform: translateY(-80px);
}

.login-form {
    width: 300px;
}

.button-container {
    display: flex;
    justify-content: center;
}
</style>