import { useCallback, useMemo, useState, useEffect } from 'react';
import Head from 'next/head';
import ArrowDownOnSquareIcon from '@heroicons/react/24/solid/ArrowDownOnSquareIcon';
import ArrowUpOnSquareIcon from '@heroicons/react/24/solid/ArrowUpOnSquareIcon';
import { Box, Button, Container, Stack, SvgIcon, Typography } from '@mui/material';
import { useSelection } from 'src/hooks/use-selection';
import { Layout as DashboardLayout } from 'src/layouts/dashboard/layout';
import { CategoriesTable } from 'src/sections/category/categories-table';
import { applyPagination } from 'src/utils/apply-pagination';
import { PopupAddCategory } from 'src/sections/category/category-add';
import { useRouter } from 'next/router';
import Cookies from 'js-cookie';
import { da } from 'date-fns/locale';


// const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/categories`, {
//   method: 'GET',
//   headers: {
//     "Content-Type": "application/json",
//     "Authorization": "Bearer " + Cookies.get("token")
//   },
// });
// const data = await res.json();

async function fetchCategories() {
  // retrieves categories data from the server
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/categories`, {
    method: 'GET',
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + Cookies.get("token")
    },
  })
  if (!res.ok) {
    throw new Error('Cannot fetch data from server')
  }
  return res
}


const useCategories = (page, rowsPerPage, data) => {
  return useMemo(
    () => {
      return applyPagination(data, page, rowsPerPage);
    },
    [page, rowsPerPage, data]
  );
};


const useCategoriesIds = (categories) => {
  return useMemo(
    () => {
      return categories.map((categorie) => categorie.id);
    },
    [categories]
  );
};


const Page = () => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [data, setData] = useState([]);
  const categories = useCategories(page, rowsPerPage, data);
  const categoriesIds = useCategoriesIds(categories);
  const categoriesSelection = useSelection(categoriesIds);

  useEffect(() => {
    fetchCategories()
      .then(res => res.json())
      .then(data => setData(data));
  }, []);

  const handlePageChange = useCallback(
    (event, value) => {
      setPage(value);
    },
    []
  );

  const handleRowsPerPageChange = useCallback(
    (event) => {
      setRowsPerPage(event.target.value);
    },
    []
  );

  return (
    <>
      <Head>
        <title>
          Categories | Spending-Webapp
        </title>
      </Head>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          py: 8
        }}
      >
        <Container maxWidth="xl">
          <Stack spacing={3}>
            <Stack
              direction="row"
              justifyContent="space-between"
              spacing={4}
            >
              <Stack spacing={1}>
                <Typography variant="h4">
                  Categories
                </Typography>
                <Stack
                  alignItems="center"
                  direction="row"
                  spacing={1}
                >
                  <Button
                    color="inherit"
                    startIcon={(
                      <SvgIcon fontSize="small">
                        <ArrowUpOnSquareIcon />
                      </SvgIcon>
                    )}
                  >
                    Import
                  </Button>
                  <Button
                    color="inherit"
                    startIcon={(
                      <SvgIcon fontSize="small">
                        <ArrowDownOnSquareIcon />
                      </SvgIcon>
                    )}
                  >
                    Export
                  </Button>
                </Stack>
              </Stack>
              <div>
                <PopupAddCategory/>
              </div>
            </Stack>
            <CategoriesTable
              count={data.length}
              items={categories}
              onDeselectAll={categoriesSelection.handleDeselectAll}
              onDeselectOne={categoriesSelection.handleDeselectOne}
              onPageChange={handlePageChange}
              onRowsPerPageChange={handleRowsPerPageChange}
              onSelectAll={categoriesSelection.handleSelectAll}
              onSelectOne={categoriesSelection.handleSelectOne}
              page={page}
              rowsPerPage={rowsPerPage}
              selected={categoriesSelection.selected}
            />
          </Stack>
        </Container>
      </Box>
    </>
  );
};

Page.getLayout = (page) => (
  <DashboardLayout>
    {page}
  </DashboardLayout>
);

export default Page;
