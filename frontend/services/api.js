// Central API configuration for the frontend
const API='http://localhost:8000';
async function api(path,options={}){const headers=options.headers||{};const token=localStorage.getItem('token');if(token)headers.Authorization='Bearer '+token;const response=await fetch(API+path,{...options,headers});const data=await response.json().catch(()=>({}));return {response,data};}
