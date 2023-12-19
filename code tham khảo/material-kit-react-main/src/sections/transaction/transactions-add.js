
import React, { useState, FormEvent }  from 'react'; 
import 'reactjs-popup/dist/index.css'; 
import { Box, Button, Container, Stack, SvgIcon, Typography, TextField, Modal, Link } from '@mui/material';
import PlusIcon from '@heroicons/react/24/solid/PlusIcon';
import { useRouter } from 'next/navigation';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useAuth } from 'src/hooks/use-auth';
import { Layout as AuthLayout } from 'src/layouts/auth/layout';


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
        date: '',
        amount: 0,
        note: '',
        type: '',
        category: '',
        submit: null
      },
      validationSchema: Yup.object({
        email: Yup
          .string()
          .max(255)
          .required('Date is required'),
        amount: Yup
          .number()
          .required('Amount must be a valid number'),
        type: Yup
          .string()
          .max(255)
          .required('Password is required'),
        category: Yup
          .string()
          .max(255)
          .required('Category is required')
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
                open={open}
                // onClose={handleClose}
                aria-labelledby="modal-modal-title"
                aria-describedby="modal-modal-description"
            >
                <Box sx={style}>
                    <h2 style={{textAlign: "center"}}>Add a transaction</h2>
                    <form
                        noValidate
                        onSubmit={formik.handleSubmit}
                    >
                        <Stack spacing={3}>
                            <TextField
                                error={!!(formik.touched.date && formik.errors.date)}
                                fullWidth
                                helperText={formik.touched.date && formik.errors.date}
                                label="Date"
                                name="date"
                                onBlur={formik.handleBlur}
                                onChange={formik.handleChange}
                                value={formik.values.date}
                            />
                            <TextField
                                error={!!(formik.touched.amount && formik.errors.amount)}
                                fullWidth
                                helperText={formik.touched.amount && formik.errors.amount}
                                label="Amount"
                                name="amount"
                                onBlur={formik.handleBlur}
                                onChange={formik.handleChange}
                                type="email"
                                value={formik.values.amount}
                            />
                            <TextField
                                // error={!!(formik.touched.password && formik.errors.password)}
                                fullWidth
                                // helperText={formik.touched.password && formik.errors.password}
                                label="Note"
                                name="note"
                                onBlur={formik.handleBlur}
                                onChange={formik.handleChange}
                                // type="password"
                                value={formik.values.note}
                            />
                            <TextField
                                error={!!(formik.touched.type && formik.errors.type)}
                                fullWidth
                                helperText={formik.touched.type && formik.errors.type}
                                label="Type"
                                name="type"
                                onBlur={formik.handleBlur}
                                onChange={formik.handleChange}
                                value={formik.values.type}
                            />
                            <TextField
                                error={!!(formik.touched.category && formik.errors.category)}
                                fullWidth
                                helperText={formik.touched.category && formik.errors.category}
                                label="Category"
                                name="category"
                                onBlur={formik.handleBlur}
                                onChange={formik.handleChange}
                                value={formik.values.category}
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