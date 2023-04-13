import Head from 'next/head'
import { Inter } from 'next/font/google'
import styles from '@/styles/Home.module.css'
import TextField from '@mui/material/TextField';
import { Box, Button, Stack } from '@mui/material';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useState } from 'react';

export default function Home() {

  const [name, setName] = useState()
  const [pw, setPW] = useState()

  const loginBtnClick = async () => {
    try {
      const login_res = await axios.post(process.env.NEXT_PUBLIC_API_BASE + "/login", {
        username: name,
        password: pw,
      }, {withCredentials: true})
  
      console.log(login_res)

      document.location = "/document_page"
    } catch (err) {
      toast.error(err.message)
    }

    
  }

  return (
    <>
      <Head>
        <title>DG Library System - Login</title>
        <meta name="description" content="DG Library System - Login" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className={styles.main}>
        
        <Box>
          <Stack spacing={2} sx={{width: "500px"}}>
            <h1>DG Library System - Login</h1>
            <TextField id="username" label="Username" variant="outlined" value={name} onChange={e=>setName(e.target.value)}/>
            <TextField id="password" label="Password" variant="outlined" type="password" value={pw} onChange={e=>setPW(e.target.value)}/>
            <Button variant="contained" onClick={loginBtnClick}>Login</Button>
          </Stack>
        </Box>
        <ToastContainer />
      </main>
    </>
  )
}
