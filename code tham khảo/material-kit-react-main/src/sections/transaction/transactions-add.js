
import React, { useState }  from 'react'; 
import Popup from 'reactjs-popup'; 
import 'reactjs-popup/dist/index.css'; 
import { Box, Button, Container, Stack, SvgIcon, Typography, Modal } from '@mui/material';
import PlusIcon from '@heroicons/react/24/solid/PlusIcon';

export const AddBtn = () => {
    return(
        <Button
            startIcon={(
                <SvgIcon fontSize="small">
                    <PlusIcon />
                </SvgIcon>
            )}
            variant="contained"
        >
            Add
        </Button>
    )
}

export const PopupGfg = () => { 
  return(
    <Popup 
        trigger={AddBtn}  
        position="right center"
    > 
        <div>Chỗ này sẽ hiện popup để thêm giao dịch</div>  
    </Popup>
  ) 
};

export const PopupAddTransaction = () => {
    const [open, setOpen] = React.useState(false);
 
    const handleClose = () => {
        setOpen(false);
    };
 
    const handleOpen = () => {
        setOpen(true);
    };
 
    return (
        <div
            style={{
                textAlign: "center",
                display: "block",
                padding: 30,
                margin: "auto",
            }}
        >
            <button type="button" onClick={handleOpen}>
                Click Me to Open Modal
            </button>
            <Modal
                onClose={handleClose}
                open={open}
                style={{
                    position: "absolute",
                    border: "2px solid #000",
                    backgroundColor: "lightgray",
                    boxShadow: "2px solid black",
                    height: 150,
                    width: 240,
                    margin: "auto",
                    padding: "2%",
                    color: "white",
                }}
            >
                <>
                    <h2>GFG</h2>
                    <p>A computer science portal!</p>
                </>
            </Modal>
        </div>
    );
}