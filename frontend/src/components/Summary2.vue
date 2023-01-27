<template>
    <div @pointermove="createchart()">
      <nav class="navbar bg-light">
    <div class="container-fluid">
      <label class="navbar-brand" @click="gohome">Kanban App</label>
      <form class="d-flex" role="search">
        <button class="btn btn-outline-success" @click="showsum">Summary</button>
        <button class="btn btn-outline-success" @click="showset">Settings</button>
          <button class="btn btn-outline-success" @click="createList">Create List</button>
          <button class="btn btn-outline-success" @click="logout">Log Out</button>
        <button class="btn btn-outline-success" @click="exportcsv">Export CSV</button>
        <a href="" :id="ololo" style="display:none"></a>
      </form>
    </div>
  </nav>
  <div>
      <form method="POST" @submit.prevent="verifyUser">
  
  <div id="app">
      <div class="card2 card--accent">
          <h2>Summary</h2>
          
          <label class="input">
            <div class="button-group">
              <button v-for="(value,key) in jdata[0]"  v-on:click="getdata(value[3])" >{{key}}</button>
              <button v-for="(value,key) in jdata[1]"  v-on:click="getdata(value[3])" >{{key}}</button>
          </div>
                    <div v-for="(value,key) in jdata[0]" >
                        <div v-html="value[0]" :id="value[3]" style="display:block"></div>
                        <canvas :id="'mychart'+value[3]" style="width:100%;max-width:600px,display:block" @pointermove="createchart(value[1],value[2],value[3])"></canvas>
              </div>    
              <div v-for="(value,key) in jdata[1]" >
                        <div :id="value[3]" style="display:none"><div v-html="value[0]" >
                        </div>
                        <canvas :id="'mychart'+value[3]" style="width:100%;max-width:600px,display:none" @pointermove="createchart(value[1],value[2],value[3])"></canvas>
                    </div>
              </div>  
                
          </label>
        
        </div>
        
        <!-- <script></script> -->
      </div>
  
  </form>
  </div>
    </div>
  </template>
  
  <script>
  import Chart from "chart.js/auto"
  export default {
      data() {
      return {
        jdata:'',
        jdata2:'',
        len:'',
        mychart:'',
        x:'',
        y:''
      }
    },
  
      created(){
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
      const url6 = `http://192.168.0.105:8080/getsumdata/${this.id}`;
              fetch(url6,{
                  method:"GET"
      })
      .then(resp=> resp.json())
      .then(data => {
        this.jdata=data;
        this.len=data[2]
        this.x=data[3]
        this.y=data[4]
      });
      this.mychart=[];
      
      this.createchart()
      this.mychart=[]
      for (let i = 0; i < this.len; i++){
            this.mychart.push(0)

        }
      },
      mounted(){
        
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
      getdata(key){
        for (let i = 1; i <= this.len; i++){
            if (i!=key){
                document.getElementById(i).style.display = "none";
                document.getElementById("mychart"+i).style.display = "none";
            }
            else{
              document.getElementById(i).style.display = "block";
              document.getElementById("mychart"+i).style.display = "block";
            }

        }
        if(key==1){
          document.getElementById("mychart").style.display="block"
        }
        else{
          document.getElementById("mychart").style.display="none"
        }
      },
      createchart(x,y,key){
        let vari="mychart"+key
        var ctx=document.getElementById(vari)
        this.mychart[key-1]=new Chart(ctx, {
          type: 'line',
          data: {
            labels: x,
            datasets: [{ 
                data: y,
                label: "Days of the month --- x-axis\n|| No of tasks completed --- y-axis ",
                borderColor: "#3e95cd",
                backgroundColor: "#7bb6dd",
              }
            ]
          },
          options : {
      scales: {
        yAxes: [{
          scaleLabel: {
            display: true,
            labelString: 'No of tasks completed'
          }
        }]
      }
    }
        });
        this.mychart[key-1];
console.log("hello")
      },
      exportcsv(){
      let id=this.$route.params.id 
    const url10=`http://192.168.0.105:8080/getlists/${id}`
    console.log(url10)
    document.getElementById("ololo").href=url10;
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