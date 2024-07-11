<template>
    <div class="book-details-container">
        <el-button plain round size="default" :icon="ArrowLeft" @click="goBack">返回</el-button>
        
        <h2>书籍详情</h2>
        <p v-if="loading">加载中</p>
        <p v-if="error">错误: {{error}}</p>
        <div v-if="book" class="book-detail">
            
            <div class="book-content">
                <div class="book-image-container">
                    <h3 class="book-title">{{book.bookTitle}}</h3>
                    <img :src="book.imageURL" class="book-image">
                </div>
                <div class="book-info">
                    <p>作者: {{book.bookAuthor}}</p>
                    <p>出版社: {{book.bookPublisher}}</p>
                    <p>ISBN: {{book.ISBN}}</p>
                    <p>出版年份: {{book.yearOfPublication}}</p>
                    <p>总评分: 
                    <el-rate
                     class="show-rating"
                     v-model="book.totalRating"
                     disabled
                     show-score
                     text-color="#ff9900"
                     scroe-template="{book.totalRating}"></el-rate>
                    </p>             
                    <router-link 
                     class="custom-router-link"
                     :to="'/book/' + book.ISBN + '/comments'"
                     >查看评论</router-link>
                </div>
            </div>
            <div v-if="introductionParts.length" class="book-introduction">
                <h4>内容简介:</h4>
                <p v-for="(part, index) in introductionParts" :key="index" >{{ part }}</p>
            </div>
            <div v-if="isLoggedIn" class="book-rating">
                <h4>评分: </h4>
                <el-rate 
                 v-model="bookRate" 
                 :allow-half="true" 
                 clearable 
                 :colors="colors" 
                 size='large' 
                 @change="submitRating"></el-rate>

                <h4>短评: </h4>
                <el-form>
                    <el-form-item size="normal">
                        <el-input
                         v-model="comment"
                         type="textarea"
                         placeholder="留下你的评论吧！" 
                         autosize
                        />
                    </el-form-item>
                </el-form>
                <el-button
                 type="plain"
                 round
                 @click="submitComment"
                >提交</el-button>
            </div>
            
        </div>
    </div>
</template>

<script setup lang="ts">
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { ArrowLeft } from '@element-plus/icons-vue';
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import router from '../router';

interface Book {
    ISBN: string,
    bookTitle: string,
    bookAuthor: string,
    bookPublisher: string,
    yearOfPublication: string,
    imageURL: string,
    introduction: string,
    totalRating: number
};


const route = useRoute();
const ISBN = route.params.ISBN
const error = ref('')
const loading = ref(false)
const book = ref<Book | null>(null)
const introductionParts = ref<string[]>([]);
const isLoggedIn = ref(false)

const bookRate = ref(0)
const colors = ref(['#99A9BF', '#F7BA2A', '#FF9900'])

const comment = ref("")
const userid = localStorage.getItem("id")
const id = JSON.parse(userid as string)

const fetchBook = async() => {
    loading.value = true;
    error.value = '';

    try{
        const response = await axios({
            method: 'POST',
            url: "http://localhost:5000/api/book",
            params:{
                isbn: ISBN
            }
        })
        book.value = response.data.data

        if (book.value?.introduction){
            introductionParts.value = book.value.introduction.split(/\r\n|\r|\n/);
        }


        console.log(book.value)
        localStorage.setItem(ISBN[0], JSON.stringify(response.data.data))
    } catch(err){
        error.value = "无法获得书籍详情";
        console.error(err)
    } finally {
        loading.value = false
    }
}

const checkLogin = () => {
    return !!(localStorage.getItem('username') && localStorage.getItem("id"));
}

const submitRating = async(rating: number) => {
    try{
        const response = await axios({
            method: "post",
            url: "http://localhost:5000/api/book/rating",
            data: {
                ISBN: ISBN,
                rating: rating,
                userid: id,
            },
            headers: {
                'ContenType': 'application/json'
            }
        })

        if (response.status === 200) {
            fetchBook();
        }
    } catch(err) {
        ElMessage({
            message: "评分提交失败",
            type: 'error',
            duration: 1000,
        })
        console.error(err)
    }
}

const submitComment = async() => {
    console.log(comment)
    try{
        const response = await axios({
            method: 'post',
            url: 'http://localhost:5000/api/comment/update',
            data: {
                "id": id,
                "ISBN": ISBN,
                "comment": comment.value,
            }
        })

        if (response.status === 200) {
            ElMessage({
                message: '评论提交成功',
                type: 'success',
                duration: 1000,
            })
        }
    } catch(err){
        ElMessage({
            message: '评论提交失败',
            type: "error",
            duration: 1000
        })
        console.error(err)
    }
}

const goBack = () =>{
    router.back();
}

onMounted(() => {
    fetchBook();
    isLoggedIn.value = checkLogin()
    // console.log(localStorage.getItem('username'))
    // console.log(isLoggedIn.value)
})

</script>

<style scoped>
.book-details-container {
    padding: 20px;
    box-sizing: border-box;
    overflow-y: auto;
}

.show-rating {
    transform: translateY(3px);
}

.book-detail {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.book-content {
    display: flex;
    align-items: flex-start;
    width: 100%;
}

.book-image-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-right: 20px;
}

.book-title {
    margin-bottom: 10px;
    text-align: center;
}

.book-image {
    width: 200px;
    height: auto;
}

.book-info {
    flex: 1;
    transform: translateY(35px);
}

.book-introduction {
    margin-top: 20px;
    width: 100%;
}

.book-rating {
    margin-top: 20px;
    width: 100%;
}

.custom-router-link {
    color: #606060;
    text-decoration: none;
}

.custom-router-link:hover {
    color: #1E90FF;
    text-decoration: none;
}
</style>