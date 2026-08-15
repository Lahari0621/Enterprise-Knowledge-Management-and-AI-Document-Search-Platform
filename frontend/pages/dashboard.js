async function showDashboard(){const {response,data}=await api('/api/me');if(!response.ok){logoutUser();return}welcome.textContent=`Welcome, ${data.name} (${data.role})`;loadDocuments();}
