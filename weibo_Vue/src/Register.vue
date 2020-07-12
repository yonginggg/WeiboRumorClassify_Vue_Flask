<template>
<body id="Login">
  <el-form class="login-container" label-position="left" label-width="0px">
    <h3 class="login_title">用户注册</h3>
    <el-form-item>
      <el-input type="text" v-model="username" auto-complete="off" placeholder="昵称"></el-input>
    </el-form-item>
    <el-form-item>
      <el-input type="text" v-model="userid" auto-complete="off" placeholder="账号"></el-input>
    </el-form-item>
    <el-form-item>
      <el-input type="password" v-model="password" auto-complete="off" placeholder="密码"></el-input>
    </el-form-item>
    <el-form-item>
      <el-input type="password" v-model="password2" auto-complete="off" placeholder="重复密码"></el-input>
    </el-form-item>

    <el-form-item style="width: 100%">
      <el-button
        type="primary"
        style="width: 100%;background: #505458;border: none; float: left"
        v-on:click="register"
      >注册</el-button>
    </el-form-item>
    <el-form-item style="width: 100%">
      <el-button
        type="primary"
        style="width: 100%;background: #505458;border: none; float: right"
        v-on:click="back"
      >返回</el-button>
    </el-form-item>
  </el-form>
</body>
</template>

<script>
// import qs from 'qs'
export default {
  name: "Login",
  data() {
    return {
        userid:'',
        username:'',
        password:'',
        password2:''
    };
  },
  methods: {
    register: function () {
      console.log("注册");
      this.$axios({
        method: 'post',
        url: 'http://127.0.0.1:8848/register',
        data: {
          userId: this.userid,
          password: this.password,
          userName: this.username,
        },
        transformRequest: [
          function (data) {
            let ret = '';
            for (let it in data) {
              ret += encodeURIComponent(it) + '=' + encodeURIComponent(data[it]) + '&'
            }
            ret = ret.substring(0, ret.lastIndexOf('&'));
            return ret
          }
        ],
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Access-Control-Allow-Origin': '*',
        }
      }).then(function (response) {
        if(response.data.port===401){
          alert(response.data.message)
        }else if(response.data.port===200){
          // aleart(response.data.message);
          // setTimeout(function (){
            window.location.href = "http://localhost:12322/#/login";
          // }, 1000);
        }
      })

    },
    back() {
      this.$router.replace({ path: "/login" });
    }
  }
};
</script>

<style>
.login-container {
  border-radius: 15px;
  background-clip: padding-box;
  margin: 90px auto;
  width: 350px;
  padding: 35px 35px 15px 35px;
  background: #fff;
  border: 1px solid #eaeaea;
  box-shadow: 0 0 25px #cac6c6;
}
.login_title {
  margin: 0px auto 40px auto;
  text-align: center;
  color: #505458;
}
#Login {
  background: url("../public/background.jpg") no-repeat;
  background-position: center;
  height: 100%;
  width: 100%;
  background-size: cover;
  position: fixed;
}
body {
  margin: 0px;
}
</style>
