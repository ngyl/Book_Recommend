<template>
  <div class="book-list-container">
    <h2>全部图书</h2>
    <el-row :gutter="20" class="book-row">
      <el-col :span="6" v-for="book in paginatedBooks" :key="book.ISBN">
        <el-card :body-style="{ padding: '20px' }" @click="viewBookDetail(book.ISBN, book.bookTitle)" class="book-card">
          <h3>{{ book.bookTitle }}</h3>
          <img :src="book.imageURL" alt="Image"/>
          <p>作者: {{ book.bookAuthor }}</p>
        </el-card>
      </el-col>
    </el-row>
    <div class="pagination-container">
      <el-pagination
       V-model: current-page="currentPage"
       :page-size="pageSize"
       layout="prev, pager, next"
       :total="books.length"
       @current-change="handlePageChange"
      />
    </div>
  </div>
</template>
  
<script setup lang="ts">
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { computed, onMounted, ref } from 'vue';
import router from '../router';


interface Book {
  ISBN: string,
  imageURL: string,
  bookTitle: string,
  bookAuthor: string,
}

const books = ref<Book[]>([]);
const currentPage = ref(1);
const pageSize = 4
const paginatedBooks = computed(() => {
  const start = (currentPage.value - 1) * pageSize 
  const end = start + pageSize;
  return books.value.slice(start, end)
})

const viewBookDetail = (ISBN: string, Book_title: string) => {
  console.log("查看图书详情: ${ISBN}");
  router.push({name: 'BookDetail',params:{ISBN, Book_title}})
}

const handlePageChange = (page: number) => {
  currentPage.value = page;
};

const fetchBooks = async() => {
  try{
    const response = await axios({
      method: "post",
      url: "http://localhost:5000/api/books"
    });

    books.value = response.data.data
    console.log(books.value)
  } catch(error) {
    console.error(error);
    ElMessage({
      message: "图书获取失败",
      type: 'error',
      duration: 1000
    })
  }
}

onMounted(() => {
  fetchBooks();
})

</script>
  
<style scoped>
.book-list-container {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.book-row {
  flex: 1;
}

.book-card {
  height: 500px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.el-card {
  cursor: pointer;
}

.el-card img {
  width: 73%;
  height: auto;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

</style>