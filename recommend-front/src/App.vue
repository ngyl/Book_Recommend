<template>
  <div class="common-layout">
    <el-container>
      <el-header height="80">
        <el-row :gutter="20" justify="space-between" align="middle">
          <el-col :span="8">
            <h1 @click="goHome" style="cursor: pointer;">图书推荐系统</h1>
          </el-col>
          <el-col :span="10" :push="10">
            <el-input 
              v-model="searchQuery" 
              placeholder="搜索书籍" 
              @keyup.enter="searchBooks" 
              style="width:260px" 
              :prefix-icon="Search"
            ></el-input>
          </el-col>
          <el-col :span="3" :push="4">
            <el-button
              size="large"
              v-if="isLoggedIn" 
              type="primary"
              icon="User"
              plain
              circle
              class="User-name"
              style="display: flex; align-items: center; justify-content: center;"
            >
            </el-button>
            <el-button
              v-else 
              type="primary" 
              @click="goToLogin">登录</el-button>
          </el-col>
          <el-col :span="3" :push="2">
            <el-button v-if="isLoggedIn" @click="logout" type="primary">注销</el-button>
            <el-button v-else @click="goToRegister">注册</el-button>
          </el-col>
        </el-row>
      </el-header>
      <el-container>
        <el-aside width="200px">
          <el-menu default-active="1" class="el-menu-vertical-demo">
            <el-menu-item index="1" @click="goToHome">全部图书</el-menu-item>
            <el-menu-item index="2" @click="goToHotBooks">热门图书</el-menu-item>
            <el-menu-item index="3" v-if="isLoggedIn" @click="goToRecommendedBooks">推荐图书</el-menu-item>
            <el-menu-item index="4" v-if="isSearched" @clik="goTosearcheResults">搜索结果</el-menu-item>
          </el-menu>
        </el-aside>
        <el-main>
          <router-view @LoggedIn="handleLoggedIn"></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
  
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Search} from '@element-plus/icons-vue';
import axios from 'axios';

const searchQuery = ref('');
const isLoggedIn = ref(false);
const isSearched = ref(false)
const username = ref("");
// const activeMenuItem = ref('1')

const router = useRouter();

const goHome = () => {
  router.push('/');
  isSearched.value = false;
};

const searchBooks = async() => {
  console.log('Search query:', searchQuery.value);
  
  if (searchQuery.value.trim() === '') {
    ElMessage({
      message:"请输入所要搜索的内容",
      type: 'warning',
      duration: 1000
    })

    return;
  }

  try{
    const response = await axios({
      method:"get",
      url:"http://localhost:5000/api/search",
      params: {
        query: searchQuery.value
      }
    })

    if (response.status === 200) {
      localStorage.setItem('searchResults', JSON.stringify(response.data.data))
      isSearched.value = true;
      router.push('/search');
    } else {
      ElMessage({
        message: '搜索失败',
        type: 'error',
        duration: 1000
      })
    }
  } catch(err){
    ElMessage({
      message: '搜索失败',
      type: 'error',
      duration: 1000
    })

    console.error(err);
  }

};

const goToLogin = () => {
  router.push('/login');
  
  // console.log(isLoggedIn)

};

const logout = async() => {
  try{
    const response = await axios({
      method: 'post',
      url: "http://localhost:5000/api/logout"
    })

    if (response.status === 200){
      ElMessage({
        message:"注销成功",
        type: 'success',
        duration: 1000
      })
      isLoggedIn.value=false;
      isSearched.value=false;
      localStorage.removeItem("username")
      localStorage.removeItem("id")
      localStorage.clear()
      router.push('/')
    }
  } catch(error){
    ElMessage({
      message: '注销失败',
      type: 'error',
      duration: 1000,
    });
    console.error(error)
  }
  
}

const goToRegister = () => {
  router.push('/register');
  isSearched.value = false;
};

const goToHome = () => {
  router.push('/');
  isSearched.value = false;
};

const goToHotBooks = () => {
  router.push('/hotbooks');
  isSearched.value = false
};

const goToRecommendedBooks = () => {
  router.push('/recommend');
  isSearched.value = false
};

const goTosearcheResults = () =>{
  router.push('/serch')
  isSearched.value = true;
}

const handleLoggedIn = (status: boolean, user: string) => {
  isLoggedIn.value = status;
  username.value = user;
};

const checkLogin = () => {
  return !!(localStorage.getItem('username') && localStorage.getItem("id"));
}

const checkLoggedIn = () => {
  isLoggedIn.value = checkLogin();
}

onMounted(() => {
  checkLoggedIn();
})

</script>

<style scoped>
.common-layout {
  position:absolute;
  top:0;
  right:0;
  bottom:0;
  left:0;
}

.el-container {
  height: 100%
}

.el-main {
  height: 90%;
}

.el-header {
  background-color: #b3c0d1;
  align-items: center;
}

.search-input {
  width: 80%;
}
.align-right {
  text-align: right;
}
</style>