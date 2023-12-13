
import React from 'react'; 
import Popup from 'reactjs-popup'; 
import 'reactjs-popup/dist/index.css'; 
import { Box, Button, Container, Stack, SvgIcon, Typography } from '@mui/material';
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
