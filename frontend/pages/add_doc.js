import Head from 'next/head'
import { Box, Button, Grid, Stack, CircularProgress } from '@mui/material';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useState } from 'react';
import {TextField} from '@mui/material';
import FileUpload from "react-mui-fileuploader"

export default function DocumentPage() {

    const [filesToUpload, setFilesToUpload] = useState([])
    const [title, setTitle] = useState("")
    const [loading, setLoading] = useState(false)

    const submitBtnClick = () => {
        setLoading(true)
        axios.post(process.env.NEXT_PUBLIC_API_BASE + "/request_upload_url", {
            title
        }, { 
            withCredentials: true 
        }).then(data => {

            const document_id = data.data.document_id
            const presigned_url = data.data.presigned_url

            var config = {
                headers: {
                  'content-type': 'application/pdf',
                }
            };

            axios.put(presigned_url, filesToUpload[0], config)
              .then(function (res1) {

                axios.post(process.env.NEXT_PUBLIC_API_BASE + "/notify_upload_complete", {document_id}, { withCredentials: true })
                    .then(function (res2) {
                        setLoading(true)
                        document.location = "/document_page"
                    })
                    .catch(function (err2) {
                        console.log(err2);
                        setLoading(false)
                    })

              })
              .catch(function (err1) {
                console.log(err1);
                setLoading(false)
              });

        }).catch(err => {
            
            console.log(err)
            setLoading(false)

        })
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
                    <TextField id="title" label="Title" variant="outlined" onChange={e => setTitle(e.target.value)} value={title}/>
                    <FileUpload
                        multiFile={true}
                        onFilesChange={handleFilesChange}
                        onContextReady={(context) => {}}
                        title={"Upload file"}
                        header={"Drop file here"}
                    />
                    <Button variant="contained" onClick={submitBtnClick} disabled={loading}>
                        {loading?  <CircularProgress/>  :"Submit"}
                    </Button>
                </Stack>
            </Box>
            
        </Box>
        </>
    )
}
