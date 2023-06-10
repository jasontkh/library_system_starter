import Head from 'next/head'
import { Box, Button, Grid, Stack } from '@mui/material';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useState, useEffect } from 'react';

export default function DocumentPage() {

  const [errMessage, setErrorMessage] = useState(null)
  const [allDocuments, setAllDocuments] = useState([])
  const [selectedDoc, setSelectedDoc] = useState(null)

  useEffect(()=>{

    axios.get(process.env.NEXT_PUBLIC_API_BASE + "/documents", { withCredentials: true }).then(data => {
      setAllDocuments(data.data.documents)
      setErrorMessage(null)
    }).catch(err => {
      setAllDocuments([])
      setErrorMessage(err.message)
    })

  }, [])

  function DocumentDetail(props) {

    const [suggested, setSuggested] = useState([])

    useEffect(()=>{
      axios.get(process.env.NEXT_PUBLIC_API_BASE + `/related_documents/${props.document.id}`, { withCredentials: true }).then(data => {
        setSuggested(data.data.documents)
        setErrorMessage(null)
      }).catch(err => {
        setSuggested([])
        setErrorMessage(err.message)
      })
    }, [])

    return (
      <Box display={"flex"} flexDirection={"column"} height={"100%"}>
        <h1>{props.document.title}</h1> 
        <div>Document ID: {props.document.id}</div>
        <iframe src={props.document.image_url} style={{flexGrow:1}}/>
        <Stack>
          <h3>Related Documents</h3>
          {suggested.map((doc)=>{
            return <Button variant="outlined" onClick={e=>{props.changeDoc(doc)}}>{doc.title}</Button>
          })}
        </Stack>
      </Box>
    )
  }
  

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
              <Box flexDirection={"row"} display={"flex"} justifyContent={"space-between"} alignItems={"center"} marginBottom={"50px"}>
                <h3>All documents</h3>
                <a href="/add_doc"><Button variant='contained'>Add New</Button></a>
              </Box>
              {errMessage ? <div> {errMessage} </div> : null}
              {allDocuments ? allDocuments.map( doc => {
                return <Box key={doc.id} sx={{cursor:"pointer", fontWeight: 400}} onClick={v=>setSelectedDoc(doc)} marginBottom={"20px"}> {doc.title} </Box>
              }) : null}
          </Grid>
          <Grid item sm={9} sx={{padding: "20px"}}>
              {selectedDoc? <DocumentDetail document={selectedDoc} changeDoc={doc=>setSelectedDoc(doc)}/>:"Please select a document"}
              
          </Grid>
      </Grid>
    </>
  )
}
