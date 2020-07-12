<template>
<body id="Login">
  <el-form class="login-container" label-position="left" label-width="0px">
    <h3 class="login_title">用户登录</h3>

    <el-form-item>
      <el-input type="text" v-model="userId" auto-complete="off" placeholder="账号"></el-input>
    </el-form-item>
    <el-form-item>
      <el-input type="password" v-model="password" auto-complete="off" placeholder="密码"></el-input>
    </el-form-item>

    <el-form-item style="width: 100%">
      <el-button
        type="primary"
        style="width: 100%;background: #505458;border: none; float: left"
        @click="login"
      >登录</el-button>
    </el-form-item>
    <el-form-item style="width: 100%">
      <el-button
        type="primary"
        style="width: 100%;background: #505458;border: none; float: right"
        @click="registered"
      >注册</el-button>
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
      userId:'',
      password:''
    };
  },
  methods: {
    login: function () {
      console.log("登录");
      this.$axios({
        method: 'post',
        url: 'http://127.0.0.1:8848/login',
        data: {
          userId: this.userId,
          password: this.password
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
          this.$message.error(response.data.message);
        }else if(response.data.port ===200){
          // alert(response.data[200]);
          localStorage.setItem("userId",response.data.userId);
          sessionStorage.setItem("userId",response.data.userId);
          localStorage.setItem("userName",response.data.userName);
          sessionStorage.setItem("userName",response.data.userName);

          window.location.href = "http://localhost:12322/#/welcome/"+sessionStorage.getItem("userId");
        }

      })

    },
    registered() {
      this.$router.replace({ path: "/register" });
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
