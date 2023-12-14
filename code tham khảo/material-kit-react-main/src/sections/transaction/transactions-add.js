
import React, { useState, FormEvent }  from 'react'; 
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
            <Button
                startIcon={(
                    <SvgIcon fontSize="small">
                        <PlusIcon />
                    </SvgIcon>
            )}
            variant="contained"
            type="button" onClick={handleOpen}
            >
                Add
            </Button>
            <Modal
                // onClose={handleClose}
                open={open}
                style={{
                    position: "absolute",
                    border: "2px solid #000",
                    backgroundColor: "lightgray",
                    boxShadow: "2px solid black",
                    height: 800,
                    width: 500,
                    margin: "auto",
                    padding: "2%",
                    color: "white",
                }}
            >
                <>
                    <h2 style={{textAlign: "center"}}>Add a transaction</h2>
                    <form style={{lineHeight: 3}}>
                        <label>Date</label>
                        <input type="text" name="date"/>
                        <br/>
                        <label>Amount</label>
                        <input type="text" name="amount"/>
                        <br/>
                        <label>Note</label>
                        <input type="text" name="note"/>
                        <br/>
                        <label>Type</label>
                        <input type="text" name="type"/>
                        <br/>
                        <label>Category</label>
                        <input type="text" name="category"/>
                        <br/>
                        {/* <button type="submit">Submit</button> */}
                        <div style={{marginTop: 40}}>
                            <Button
                                variant="contained"
                                type="submit"
                                style={{float: "left"}}
                            >
                                Submit
                            </Button>
                            <Button
                                variant="contained"
                                type="button" onClick={handleClose}
                                style={{float: "right"}}
                            >
                                Close
                            </Button>
                        </div>
                    </form>
                </>
            </Modal>
        </div>
    );
}