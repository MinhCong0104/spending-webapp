import React, { useState, FormEvent }  from 'react'; 
// import 'reactjs-popup/dist/index.css'; 
import { 
    Box, 
    Button, 
    Stack, 
    SvgIcon, 
    Typography, 
    TextField, 
    Modal, 
} from '@mui/material';
import PlusIcon from '@heroicons/react/24/solid/PlusIcon';
import { useRouter } from 'next/navigation';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useAuth } from 'src/hooks/use-auth';
import { Layout as AuthLayout } from 'src/layouts/auth/layout';
import Cookies from 'js-cookie';
import SelectVariants from './category-select-type';


const types = ['income', 'spend', 'save']


const style = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 400,
    bgcolor: 'background.paper',
    border: '2px solid #000',
    boxShadow: 24,
    p: 4,
  };


export const PopupAddCategory = () => {
    const [open, setOpen] = useState(false);
 
    const handleClose = () => {
        setOpen(false);
    };
 
    const handleOpen = () => {
        setOpen(true);
    };

    const router = useRouter();
    const auth = useAuth();
    const formik = useFormik({
      initialValues: {
        name: '',
        type: '',
        note: '',
      },
      validationSchema: Yup.object({
        name: Yup
          .string()
          .max(255)
          .required('Name name is required'),
        // type: Yup
        //   .string()
        //   .required('Type is required'),
      }),
      onSubmit: async (values, helpers) => {
        try {
          console.log()
          const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/categories`, {
            method: "POST",
            body: JSON.stringify(values),
            headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + Cookies.get("token")
            }
          })
          if (res.ok) {
            setOpen(false);
          }
        } catch (err) {
          console.log(err)
          helpers.setStatus({ success: false });
          helpers.setErrors({ submit: err.message });
          helpers.setSubmitting(false);
          }
      }
    });
 
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
                open={open}
                // onClose={handleClose}
                aria-labelledby="modal-modal-title"
                aria-describedby="modal-modal-description"
            >
                <Box sx={style}>
                    <h2 style={{textAlign: "center"}}>Add a category</h2>
                    <form
                        noValidate
                        onSubmit={formik.handleSubmit}
                    >
                        <Stack spacing={3}>
                            <TextField
                                error={!!(formik.touched.name && formik.errors.name)}
                                fullWidth
                                helperText={formik.touched.name && formik.errors.name}
                                label="Name"
                                name="name"
                                onBlur={formik.handleBlur}
                                onChange={formik.handleChange}
                                value={formik.values.name}
                            />
                            <TextField
                                fullWidth
                                label="Note"
                                name="note"
                                onBlur={formik.handleBlur}
                                onChange={formik.handleChange}
                                value={formik.values.note}
                            />
                            <SelectVariants 
                                name="Type"
                                valuesList={types}
                                // value={formik.value.type}
                            />
                        </Stack>

                        {formik.errors.submit && (
                            <Typography
                                color="error"
                                sx={{ mt: 3 }}
                                variant="body2"
                            >
                                {formik.errors.submit}
                            </Typography>
                        )}
                        <Button
                            fullWidth
                            size="large"
                            sx={{ mt: 3 }}
                            type="submit"
                            variant="contained"
                        >
                            Submit
                        </Button>
                        <Button
                            fullWidth
                            size="large"
                            sx={{ mt: 3 }}
                            type="button"
                            onClick={handleClose}
                            color="inherit"
                            variant="contained"
                        >
                            Cancel
                        </Button>
                    </form>
                </Box>
            </Modal>
        </div>
    );
}