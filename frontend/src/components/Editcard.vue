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
          <h2>Editing Card</h2>
          <label class="input">
              
              <input class="input__field" type="text" title="email" name="email" v-model="lname" placeholder="{{lname}}" />
              <h1></h1>
              <textarea class="input__field" type="text" title="email" name="email" v-model="summary" placeholder="{{summary}}" />
              <h1></h1>
              
              <input class="input__field" type="date" title="email" name="email" v-model="date" placeholder="{{date}}" />
              <h1></h1>
          </label>
        
          <div class="button-group">
              <button type="submit" @click="nextcard" >Edit Card</button>
          </div>
        </div>
      </div>
      <div class="alert alert-primary" v-if="error" role="alert">
          Card couldnt be edited, Try again
  </div>
  <div class="alert alert-success" v-if="error2" role="alert">
          Card added
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  </div>
  
  </form>
  </div>
    </div>
  </template>
  
  <script>
  export default {
      data() {
      return {
        lname:'',
        summary:'',
        date:'',
        error:false,
        id:'',
        flname:'',
        cname:''
      }
    },
  
      created(){
          console.log()
          this.id=this.$route.params.id
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
      this.flname=this.$route.params.lisname
      this.lname=this.$route.params.cname
      this.cname=this.$route.params.cname
      this.summary=this.$route.params.summary
      this.date=this.$route.params.date
      },
      methods:{
      createList(){
          let id=this.$route.params.id
          this.$router.push(`/createlist/${id}`)
      },
      // nextcard(){
      //     console.log('hello')
      // }
      nextcard(){
          let id=this.$route.params.id
          const url = `http://192.168.0.105:8080/editcard/${id}/${this.flname}/${this.summary}/${this.date}/${this.lname}/${this.cname}`;
          fetch(url,{
                  method:"GET"
      })
      .then(resp=> resp.json())
      .then(data => {
        if (data.commit=="True"){
        let id=this.$route.params.id
          this.$router.push(`/dashboard/${id}`)
        }
        else{
          this.error=true
        }
      });
  
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