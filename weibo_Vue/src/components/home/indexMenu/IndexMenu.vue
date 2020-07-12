<template>
  <div class="cantainer" id="profile-nav">
    <div class="profile-nav-wrap">
      <div class="profile-heading">
        <profile-heading :bigHeadShow="bigHeadShow"></profile-heading>
      </div>
      <div class="blogger-about">
        <BloggerInfo v-if="!isShowSearchBar" @fileclick="showSearchBar" class="animated fadeInUp"></BloggerInfo>
        <SearchBar
          v-else
          :propText="searchBarText"
          @onClose="closeSearchBar"
          class="animated bounceInLeft"
          ref="searchBar"
        ></SearchBar>
      </div>
      <div class="profile-nav-list">
        <menu-item class="menu-item" :title="my" :number="skillTotal" :index="welcome"></menu-item>
        <menu-item class="menu-item" title="All" :number="lifeTotal" index="/life"></menu-item>
      </div>
      <div class="right-btn">
        <div class="right">
          <blog-button @click="saveArticle" >分享</blog-button>
        </div>
      </div>
      <blog-dialog
              @close="closeDialog"
              @submit="handleSubmit"
              v-if="dialogVisible"
              confirm="立即发布"
              title="分享动态"
      >
        <form-item label="内容">
          <blog-input size="small" v-model="hostKey"></blog-input>
        </form-item>
        <form-item label="个人分类">
          <div class="scroller">
            <checkbox-group v-model="checkList">
              <checkbox
                      v-for="(item,index) in checkboxData"
                      v-bind:key="index"
                      :label="item.Name"
                      :value="item.ID"
              ></checkbox>
            </checkbox-group>
          </div>
        </form-item>
        <!--      <form-item label="标签">-->
        <!--        <tag-inputer :max="3" @change="handleOnchange"></tag-inputer>-->
        <!--      </form-item>-->
        <!--      <form-item label="文章类型">-->
        <!--        <radio-group v-model="radioIschecked">-->
        <!--          <radio label="skill" value="0"></radio>-->
        <!--          <radio label="life" value="1"></radio>-->
        <!--        </radio-group>-->
        <!--      </form-item>-->
      </blog-dialog>
    </div>
  </div>
</template>
<script>
import MenuItem from "@/components/home/indexMenu/children/MenuItem.vue";
import ProfileHeading from "@/components/home/indexMenu/children/ProfileHeading.vue";
import BloggerInfo from "@/components/home/indexMenu/children/BloggerInfo.vue";
import SearchBar from "@/components/home/indexMenu/children/SearchBar.vue";
import { apiArticleCount } from "@/api/article";
import BlogButton from "@/components/commons/button/BlogButton.vue";
import { apiArticleSave } from "@/api/article";
import { apiGetCategoryList } from "@/api/category";
import Checkbox from "@/components/commons/checkbox/Checkbox.vue";
import CheckboxGroup from "@/components/commons/checkbox/CheckboxGroup.vue";
import FormItem from "@/components/commons/formItem/FormItem.vue";
import BlogInput from "@/components/commons/input/BlogInput.vue";
import BlogDialog from "@/components/commons/dialog/BlogDialog.vue";
export default {
  data() {
    return {
      fixedFlag: false,
      bigHeadShow: true,
      lifeTotal: 0,
      skillTotal: 0,
      dialogVisible: false,
      checkList: [],
      hostKey: "",
      checkboxData: [],
      welcome:"/welcome/"+sessionStorage.getItem("userId"),
      my:"",
      Name:"",
    };
  },
  props: ["isShowSearchBar", "searchBarText"],
  components: {
    MenuItem,
    BloggerInfo,
    ProfileHeading,
    BlogButton,
    SearchBar,
    Checkbox,
    CheckboxGroup,
    FormItem,
    BlogInput,
    BlogDialog
  },
  methods: {
    async getCategoryList() {
      try {
        const res = await apiGetCategoryList({}, null);
        this.checkboxData = res.Data.List;
      } catch (e) {
        this.$message.error(e.Msg);
      }
    },
    closeDialog() {
      this.dialogVisible = false;
    },
    async handleSubmit() {
      // if (this.title.trim() === "") {
      //   this.$message.error("文章标题不能为空");
      //   return;
      // }
      // if (this.content.trim() === "") {
      //   this.$message.error("文章内容不能为空");
      //   return;
      // }

      if (this.checkList.length === 0) {
        this.$message.error("请至少选择一个文章分类");
        return;
      }
      if (this.checkList.length > 1) {
        this.$message.error("最多选择一个文章分类");
        return;
      }
      if (this.hostKey === "") {
        this.$message.error("请输入内容");
        return;
      }
      try {
        const res = await apiArticleSave(
                {
                  // Content: this.content,
                  CategoryIDs: this.checkList.join(","),
                  // Title: this.title,
                  // Personal: this.radioIschecked, // personal 0 技能文章 1 生活文章
                  // Tags: this.tags.join(","),
                  HostKey: this.hostKey,
                  userID: localStorage.getItem("userId"),
                  userName: localStorage.getItem("userName")
                },
                null
        );
        this.$message.success(res.Msg);
        this.hostKey = "";
        this.dialogVisible = false;
        setTimeout(function (){
          // this.$router.replace({ path: "/login" });
          location.reload();
        }, 1000);
      } catch (e) {
        this.$message.error(e.Msg);
      }
    },
    saveArticle() {
      this.dialogVisible = true;
    },
    closeSearchBar(flag) {
      this.$emit("closeSearchBar", flag);
    },
    pushArticleEdit() {
      this.$router.push({
        path: "/article/edit/0"
      });
    },
    showSearchBar() {
      this.$emit("showSearchBar");
    },
    handleScroll() {
      const scrollTop = document.documentElement.scrollTop;
      const scrollHeight = document.documentElement.scrollHeight;
      const clientHeight = document.documentElement.clientHeight;
      const profileObj = document.getElementById("profile-nav");
      const fakeAreaObj = document.getElementById("fake-area");
      if (scrollTop > 296) {
        if (!this.fixedFlag) {
          this.bigHeadShow = false;
          profileObj.style.position = "fixed";
          profileObj.style.top = "77px";
          fakeAreaObj.style.position = "fixed";
          fakeAreaObj.style.top = "47px";
          this.fixedFlag = true;
        }
      } else {
        if (this.fixedFlag) {
          this.bigHeadShow = true;
          profileObj.style.position = "";
          profileObj.style.top = "";
          fakeAreaObj.style.position = "";
          fakeAreaObj.style.top = "";
          this.fixedFlag = false;
        }
      }
    },
    getArticleCount() {
      if (localStorage.getItem("lifeTotal")) {
        this.lifeTotal = parseInt(localStorage.getItem("lifeTotal"));
      }
      if (localStorage.getItem("skillTotal")) {
        this.skillTotal = parseInt(localStorage.getItem("skillTotal"));
      }
    },
    async getArticleCount() {
      const res = await apiArticleCount(
        {
          // Personal: sessionStorage.getItem("userId")
          Personal: this.$route.params.id
        },
        null
      );
      this.lifeTotal = res.Data.commentSum;
      this.skillTotal = res.Data.articleSum;
      this.Name = res.Data.Name;
    }
  },
  created() {
    window.addEventListener("scroll", this.handleScroll);
    this.getArticleCount();
    this.getCategoryList();
  },
  mounted() {
    if(sessionStorage.getItem('userId')===localStorage.getItem('userId')){
      this.my='My'
    }else{
      this.my='His'
    }
  },
  beforeDestroy() {
    window.removeEventListener("scroll", this.handleScroll);
  }
};
</script>
<style scoped lang="scss">
.fake-area {
  width: 100%;
  height: $height-fake-area;
  background-color: #f3f6f8;
}
.cantainer {
  width: 100%;
  background-color: #ffffff;
  display: flex;
  justify-content: center;
  height: $height-profile-nav-wrap;
  border-bottom: 1px solid #cccccc;
  border-top: 1px solid #cccccc;
  box-shadow: 1px 1px 2px #cbcbcb;
  .profile-nav-wrap {
    width: 1220px;
    position: relative;
    .blogger-about {
      position: absolute;
      top: 100px;
    }
    .profile-heading {
      position: absolute;
      height: 62px;
      left: 0px;
      width: 310px;
    }
    .profile-nav-list {
      position: absolute;
      height: 62px;
      left: 310px;
      width: 610px;
      .menu-item {
        display: inline-block;
      }
    }
    .right-btn {
      position: absolute;
      right: 0px;
      width: 300px;
      top: 10px;
      .right {
        position: absolute;
        right: 0px;
      }
    }
  }
}
</style>
