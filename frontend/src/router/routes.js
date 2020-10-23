import MainLayout from 'layouts/MainLayout.vue'

const Index = () => import(/* webpackChunkName: "base" */ 'pages/Index.vue')
const About = () => import(/* webpackChunkName: "base" */ 'pages/About.vue')

const Login = () => import(/* webpackChunkName: "user" */ 'pages/Login.vue')

const BaseContainer = () => import(/* webpackChunkName: "base" */ 'pages/BaseContainer.vue')

const CollectionInfo = () => import(/* webpackChunkName: "collection" */ 'pages/CollectionInfo.vue')

const DatasetInfo = () => import(/* webpackChunkName: "dataset" */ 'pages/DatasetInfo.vue')

const OrderInfo = () => import(/* webpackChunkName: "order" */ 'pages/OrderInfo.vue')

const EntryBrowser = () => import(/* webpackChunkName: "browser" */ 'pages/EntryBrowser.vue')

const UserManager = () => import(/* webpackChunkName: "admin" */ 'pages/UserManager.vue')

const CurrentUser = () => import(/* webpackChunkName: "current" */ 'pages/CurrentUser.vue')

const routes = [
  {
    path: '/',
    component:  MainLayout,
    children: [
      { path: '', component: Index, name: 'Home'},
      { path: 'about', component: About, name: 'About' },
      { path: 'guide', component: About, name: 'User Guide' },
      { path: 'login', component: Login, name: 'Login' },
    ]
  },

  {
    path: '/datasets',
    component:  MainLayout,
    children: [
      {
        path: '',
        component: EntryBrowser,
        name: 'Dataset Browser',
        props: { 'entryType': 'dataset'}
      },
      {
        path: ':uuid([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
        component: DatasetInfo,
        props: true,
        name: 'Dataset About'
      },
      {
        path: 'new',
        component: DatasetInfo,
        props: {'uuid': ''},
        name: 'Dataset New'
      },
    ]
  },

  {
    path: '/me',
    component:  MainLayout,
    children: [
      {
        path: '',
        component: CurrentUser,
        name: 'About Current User',
      },
    ]
  },
  
  {
    path: '/orders',
    component:  MainLayout,
    meta: {
      'accessReq': ['ordersSelf'],
    },
    children: [
      {
        path: '',
        component: EntryBrowser,
        name: 'Order Browser',
        props: { 'entryType': 'order'}
      },
      {
        path: ':uuid([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
        component: OrderInfo,
        props: true,
        name: 'Order About'
      },
      {
        path: 'new',
        component: OrderInfo,
        props: {'uuid': ''},
        name: 'Order New'
      },
    ]
  },

  {
    path: '/collections',
    component:  MainLayout,
    children: [
      {
        path: '',
        component: EntryBrowser,
        name: 'Collection Browser',
        props: { 'entryType': 'collection'}
      },
      {
        path: ':uuid([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
        component: CollectionInfo,
        props: true,
        name: 'Collection About'
      },
      {
        path: 'new',
        component: CollectionInfo,
        props: {'uuid': ''},
        name: 'Collection New'
      },
    ]
  },

  {
    path: '/admin',
    component: MainLayout,
    children: [
      {
        path: 'user',
        component: UserManager,
        meta: {
          'accessReq': ['userManagement'],
        },
      },
    ]
  },

  {
    path: '*',
    component: () => import('pages/Error404.vue'),
  }
]

export default routes
