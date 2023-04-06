import Head from 'next/head'
import { Box, Button, Grid, Stack } from '@mui/material';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useState } from 'react';
import {TextField} from '@mui/material';

export default function DocumentPage() {

    const [filesToUpload, setFilesToUpload] = useState([])

    const submitBtnClick = () => {
        
    }

    const handleFilesChange = (files) => {
        setFilesToUpload([ ...files ])
    };

    return (
        <>
        <Head>
            <title>DG Library System - Add document</title>
            <meta name="description" content="DG Library System - Add document" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <link rel="icon" href="/favicon.ico" />
        </Head>

        <Box container sx={{height: "100vh", padding:"20px", display:"flex", justifyContent:"center"}}>
            <Box sx={{width: "500px", maxWidth: "100%"}}>
                <Stack spacing={2}>
                    <h1>Add document</h1>
                    <TextField id="title" label="title" variant="outlined" />
                    <FileUpload
                        multiFile={true}
                        onFilesChange={handleFilesChange}
                        onContextReady={(context) => {}}
                    />
                    <Button variant="contained" onClick={submitBtnClick}>Submit</Button>
                </Stack>
            </Box>
            
        </Box>
        </>
    )
}
