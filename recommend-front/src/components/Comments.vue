<template>
    <div class="comments-container">
        <el-button plain round :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h3>评论</h3>
        <div v-if="loading">加载中...</div>
        <div v-if="error">错误: {{ error }}</div>
        <ul v-if="comments.length">
            <li v-for="comment in paginatedComments" :key="comment.id">
                <p><strong>{{ comment.username }}</strong></p>
                <p>{{ comment.comment }}</p>
            </li>
        </ul>
        <div v-else>暂无评论</div>
        <el-pagination
         v-if="comments.length > 10"
         V-model: current-page="currentPage"
         layout="prev, pager, next"
         :total="comments.length"
         :page-size="pageSize"
         @current-change="handlePageChange"
        ></el-pagination>
    </div>
    
</template>

<script setup lang="ts">
import axios from 'axios';
import { computed, ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { ArrowLeft } from '@element-plus/icons-vue';
import router from '../router';


interface Comment {
id: number;
username: string;
ISBN: string;
comment: string;
}

const route = useRoute();
const ISBN = route.params.ISBN;
const comments = ref<Comment[]>([]);
const loading = ref(false);
const error = ref('');
const currentPage = ref(1);
const pageSize = 10;


const fetchComments = async () => {
loading.value = true;
error.value = '';

try {
    const response = await axios({
    method: 'post',
    url: `http://localhost:5000/api/comments`,
    data:{
        "ISBN": ISBN,
    }
    });
    comments.value = response.data.data;

    console.log(response.data.data)
} catch (err) {
    error.value = '无法获得评论信息';
    console.error(err);
} finally {
    loading.value = false;
}
};

const paginatedComments = computed(() => {
    const start = (currentPage.value - 1) * pageSize;
    const end = start + pageSize;
    return comments.value.slice(start, end);
});

const handlePageChange = (page: number) => {
    currentPage.value = page;
}

const goBack = () => {
    router.back();
}

onMounted(() => {
    fetchComments();
});
</script>

<style scoped>
.comments-container {
    padding: 20px;
}
</style>