import Head from 'next/head'
import { Box, Button, Grid, Stack } from '@mui/material';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useState } from 'react';

export default function DocumentPage() {

  return (
    <>
      <Head>
        <title>DG Library System - Viewer</title>
        <meta name="description" content="DG Library System - Viewer" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
        
      <Grid container sx={{height: "100vh"}}>
          <Grid item sm={3} sx={{borderRight: "solid 1px grey", padding: "20px"}}>
              <Box flexDirection={"row"} display={"flex"} justifyContent={"space-between"} alignItems={"center"}>
                <h3>All documents</h3>
                <a href="/add_doc"><Button variant='contained'>Add New</Button></a>
              </Box>
          </Grid>
          <Grid item sm={9} sx={{padding: "20px"}}>
              Please select a document
          </Grid>
      </Grid>
    </>
  )
}
