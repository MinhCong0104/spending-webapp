import { useCallback, useMemo, useState } from 'react';
import Head from 'next/head';
import ArrowDownOnSquareIcon from '@heroicons/react/24/solid/ArrowDownOnSquareIcon';
import ArrowUpOnSquareIcon from '@heroicons/react/24/solid/ArrowUpOnSquareIcon';
import { Box, Button, Container, Stack, SvgIcon, Typography } from '@mui/material';
import { useSelection } from 'src/hooks/use-selection';
import { Layout as DashboardLayout } from 'src/layouts/dashboard/layout';
import { CategoriesTable } from 'src/sections/category/categories-table';
import { applyPagination } from 'src/utils/apply-pagination';
import { PopupAddCategory } from 'src/sections/category/category-add';

const now = new Date();

const data = [
  {
    id: '6e887ac47eed253091be10cb',
    category: 'Tiền ăn',
    type: 'Spend',
    note: 'Dùng khi giao dịch là trả tiền ăn uống hàng ngày'
  },
  {
    id: '6e887b209c28ac3dd97f6db5',
    category: 'Tiền nhà',
    type: 'Spend',
    note: 'Dùng khi giao dịch là trả tiền nhà (điện, nước, dịch vụ, tiền thuê phòng)'
  },
  {
    id: '6e887b7602bdbc4dbb234b27',
    category: 'Tiêu dùng',
    type: 'Spend',
    note: 'Dùng khi giao dịch là trả tiền đi chơi, ăn vặt, chi tiêu linh tinh...'
  },
  {
    id: '6e86809283e28b96d2d38537',
    category: 'Mua đồ',
    type: 'Spend',
    note: 'Dùng khi giao dịch là trả tiền mua sắm quần áo, đồ gia dụng'
  },
  {
    id: '6e86805e2bafd54f66cc95c3',
    category: 'Lương',
    type: 'Income',
    note: 'Dùng khi giao dịch là góp tiền lương vào để chi tiêu'
  },
  {
    id: '6e887a1fbefd7938eea9c981',
    category: 'Rút tiền tiết kiệm',
    type: 'Income',
    note: 'Dùng khi giao dịch là rút tiền tiết kiệm để chi tiêu'
  },
  {
    id: '6e887a1fbefd7938eea9axz1',
    category: 'Tiết kiệm',
    type: 'Save',
    note: 'Dùng khi giao dịch là gửi tiền tiết kiệm'
  },
];

const useCategories = (page, rowsPerPage) => {
  return useMemo(
    () => {
      return applyPagination(data, page, rowsPerPage);
    },
    [page, rowsPerPage]
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
  const categories = useCategories(page, rowsPerPage);
  const categoriesIds = useCategoriesIds(categories);
  const categoriesSelection = useSelection(categoriesIds);

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
            {/* <TransactionsSearch /> */}
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
