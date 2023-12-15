
import React, { useState, FormEvent }  from 'react'; 
import Popup from 'reactjs-popup'; 
import 'reactjs-popup/dist/index.css'; 
import { Box, Button, Container, Stack, SvgIcon, Typography, Modal, TextField, Link } from '@mui/material';
import PlusIcon from '@heroicons/react/24/solid/PlusIcon';
// import { transactionForm } from './transactions-form';
import Head from 'next/head';
import NextLink from 'next/link';
import { useRouter } from 'next/navigation';
import { useFormik } from 'formik';
import * as Yup from 'yup';
// import { Box, Button, Link, Stack, TextField, Typography } from '@mui/material';
import { useAuth } from 'src/hooks/use-auth';
import { Layout as AuthLayout } from 'src/layouts/auth/layout';

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

    const router = useRouter();
    const auth = useAuth();
    const formik = useFormik({
      initialValues: {
        email: '',
        name: '',
        password: '',
        submit: null
      },
      validationSchema: Yup.object({
        email: Yup
          .string()
          .email('Must be a valid email')
          .max(255)
          .required('Email is required'),
        name: Yup
          .string()
          .max(255)
          .required('Name is required'),
        password: Yup
          .string()
          .max(255)
          .required('Password is required')
      }),
      onSubmit: async (values, helpers) => {
        try {
          await auth.signUp(values.email, values.name, values.password);
          router.push('/');
        } catch (err) {
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
                // onClose={handleClose}
                open={open}
                style={{
                    position: "absolute",
                    border: "2px solid #000",
                    backgroundColor: "lightgray",
                    boxShadow: "2px solid black",
                    height: 500,
                    width: 400,
                    margin: "auto",
                    padding: "2%",
                    color: "white",
                }}
            >
                <>
                    <h2 style={{textAlign: "center"}}>Add a transaction</h2>
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
                                error={!!(formik.touched.email && formik.errors.email)}
                                fullWidth
                                helperText={formik.touched.email && formik.errors.email}
                                label="Email Address"
                                name="email"
                                onBlur={formik.handleBlur}
                                onChange={formik.handleChange}
                                type="email"
                                value={formik.values.email}
                            />
                            <TextField
                                error={!!(formik.touched.password && formik.errors.password)}
                                fullWidth
                                helperText={formik.touched.password && formik.errors.password}
                                label="Password"
                                name="password"
                                onBlur={formik.handleBlur}
                                onChange={formik.handleChange}
                                type="password"
                                value={formik.values.password}
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
                            Continue
                        </Button>
                    </form>
                </>
            </Modal>
        </div>
    );
}