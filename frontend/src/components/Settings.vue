<template>
    <div>
      <nav class="navbar bg-light">
    <div class="container-fluid">
      <label class="navbar-brand" @click="gohome">Kanban App</label>
      <form class="d-flex" role="search">
        <button class="btn btn-outline-success" @click="showsum">Summary</button>
        <button class="btn btn-outline-success" @click="showset">Settings</button>
          <button class="btn btn-outline-success" @click="createList">Create List</button>
          <button class="btn btn-outline-success" @click="logout">Log Out</button>
        <button class="btn btn-outline-success" @click="exportcsv">Export CSV</button>
        <a href="" id="ololo" style="display:none"></a>
      </form>
    </div>
  </nav>
  <div>
      <form method="POST" @submit.prevent="verifyUser">
  
  <div id="app">
      <div class="card2 card--accent">
          <h2>Details</h2>
          <label class="input">
              Name:
              <input class="input__field" type="text" title="name" name="name" v-model="name" placeholder="{{ name }}" />
              <h1></h1>
              Email:
              <input class="input__field" type="text" title="email" name="email" v-model="email" placeholder="{{ email }}" />
              <h1></h1>
              Password:
              <input class="input__field" type="text" title="passwd" name="passwd" v-model="passwd" placeholder="{{ passwd }}" />
              <h1></h1>
              Email Preference:<br> <br>
              <input type="radio" v-model="check" value="1" id="check1">HTML
              <input type="radio" v-model="check" value="0" id="check2">PDF
              <h1></h1>
          </label>
          <div class="alert alert-success" id="alert" style="display:none" role="alert">
        Username already exist, chose another one.
</div>
          <div class="button-group">
              <button type="submit" @click="changeuserdata" >Submit</button>
          </div>
        </div>
      </div>
  
  </form>
  </div>
    </div>
  </template>
  
  <script>
  export default {
      data() {
      return {
        name:'',
        email:'',
        passwd:'',
        check:'',
        id:'',
        rep_type:''
      }
    },
  
      created(){
          console.log();
          this.id=this.$route.params.id;
          const url = `http://192.168.0.105:8080/getauth/${this.id}`;
              fetch(url,{
                  method:"GET"
      })
      .then(resp=> resp.json())
      .then(data => {
        if (data.auth=="False"){
          this.$router.push('/')
        }
      });
      const url6 = `http://192.168.0.105:8080/getuserdata/${this.id}`;
              fetch(url6,{
                  method:"GET"
      })
      .then(resp=> resp.json())
      .then(data => {
        const dat=(data)
        this.name=dat.name;
        this.email=dat.email;
        this.passwd=dat.passwd;
        this.rep_type=dat.rep_type;
        if(this.rep_type=="1"){
          document.getElementById("check1").checked = true;
          this.check=1
        }else{
          this.check=0
          document.getElementById("check2").checked = true;
        }
        console.log(data)
      });
          
      },
      methods:{
      createList(){
          let id=this.$route.params.id
          this.$router.push(`/createlist/${id}`)
      },
      gohome(){
          let id=this.$route.params.id
          this.$router.push(`/dashboard/${id}`)
          
      },
      logout(key){
      let id=this.$route.params.id 
      const url3=`http://192.168.0.105:8080/logout/${id}`
      fetch(url3,{
                  method:"GET"
      })
      .then(resp=> resp.json())
      .then(data => {
          console.log('Logged out')
          this.gohome();
      });
      },
      changeuserdata(){
      let id=this.$route.params.id 
      console.log(this.name,this.email,this.passwd,this.check)
      const url3=`http://192.168.0.105:8080/changedata/${id}/${this.name}/${this.email}/${this.passwd}/${this.check}`
      fetch(url3,{
                  method:"GET"
      })
      .then(resp=> resp.json())
      .then(data => {
        if (data.commit=="True"){
          console.log('changed settings')
          this.gohome();
        }
        else{
          document.getElementById("alert").style.display="block"
        }

      });
      },
      exportcsv(key){
      let id=this.$route.params.id 
    const url4=`http://192.168.0.105:8080/getlists/${id}`
    document.getElementById("ololo").href=url4;
    document.getElementById("ololo").click();

    },
    exportlist(key){
      let id=this.$route.params.id 
    const url5=`http://192.168.0.105:8080/getlis/${id}/${key}`
    document.getElementById("ololo").href=url5;
    document.getElementById("ololo").click();

    },
    showset(){
        let id=this.$route.params.id
        this.$router.push(`/settings/${id}`)
    },
    showsum(){
        let id=this.$route.params.id
        this.$router.push(`/summary/${id}`)
    },
    }
  }
  </script>
  
  <style>
  
  </style>