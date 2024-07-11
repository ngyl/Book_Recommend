import { createRouter, createWebHistory } from "vue-router"

const routes = [
    {
        path: '/',
        name: 'Home',
        component: () => import('../components/Home.vue'),
        meta: {
            title: '图书推荐系统'
        }
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import('../components/Login.vue'),
        meta: {
            title: '图书推荐系统'
        }
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('../components/Register.vue'),
        meta: {
            title: '图书推荐系统'
        }
    },
    {
        path: '/book/:ISBN',
        name: 'BookDetail',
        component: () => import('../components/BookDetail.vue'),
        meta: {
            title: '书籍详情'
        },
    },
    {
        path: '/book/:ISBN/comments',
        name: 'BookComments',
        component: () => import('../components/Comments.vue'),
        meta: {
            title: '评论详情'
        }
    },
    {
        path: '/hotbooks',
        name: 'HotBooks',
        component: () => import('../components/HotBooks.vue'),
        meta: {
            title: '图书推荐系统:热门图书'
        }
    },
    {
        path: '/search',
        name: 'Search',
        component: () => import('../components/SearchedBooks.vue'),
        meta:{
            title: '图书推荐系统:搜索结果'
        }
    },
    {
        path: '/recommend',
        name: 'RecommendBooks',
        component: () => import('../components/RecommendBooks.vue'),
        meta:{
            title: '图书推荐系统'
        }
    }
    
]

const router = createRouter({
    history : createWebHistory(),
    routes
})

router.beforeEach((to, _from, next) => {
    const title = to.meta.title as string
    if (to.meta.title){
        document.title = title
    }

    next();
});


export default router