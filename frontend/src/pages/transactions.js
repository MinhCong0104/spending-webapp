import { useCallback, useMemo, useState } from 'react';
import Head from 'next/head';
import { subDays, subHours } from 'date-fns';
import ArrowDownOnSquareIcon from '@heroicons/react/24/solid/ArrowDownOnSquareIcon';
import ArrowUpOnSquareIcon from '@heroicons/react/24/solid/ArrowUpOnSquareIcon';
import { Box, Button, Container, Stack, SvgIcon, Typography } from '@mui/material';
import { useSelection } from 'src/hooks/use-selection';
import { Layout as DashboardLayout } from 'src/layouts/dashboard/layout';
import { TransactionsTable } from 'src/sections/transaction/transactions-table';
import { TransactionsSearch } from 'src/sections/transaction/transactions-search';
import { applyPagination } from 'src/utils/apply-pagination';
import { PopupGfg } from 'src/sections/transaction/transactions-add';
import { PopupAddTransaction } from 'src/sections/transaction/transactions-add';

const now = new Date();

const data = [
  {
    id: '5e887ac47eed253091be10cb',
    date: subDays(subHours(now, 7), 1).getTime(),
    amount: -10000,
    note: 'Mua rau',
    type: 'Chi tiêu',
    category: 'Tiền ăn'
  },
  {
    id: '5e887b209c28ac3dd97f6db5',
    date: subDays(subHours(now, 1), 2).getTime(),
    amount: -100000,
    note: 'Xem phim',
    type: 'Chi tiêu',
    category: 'Tiêu dùng'
  },
  {
    id: '5e887b7602bdbc4dbb234b27',
    date: subDays(subHours(now, 8), 2).getTime(),
    amount: 6000000,
    note: 'Lương của Phương',
    type: 'Thu nhập',
    category: 'Lương'
  },
  {
    id: '5e86809283e28b96d2d38537',
    date: subDays(subHours(now, 11), 2).getTime(),
    amount: -5000000,
    note: 'Gửi tiết kiệm eInvest',
    type: 'Tiết kiệm',
    category: 'Tiết kiệm'
  },
  {
    id: '5e86805e2bafd54f66cc95c3',
    date: subDays(subHours(now, 7), 3).getTime(),
    amount: -300000,
    note: 'Ăn lẩu',
    type: 'Chi tiêu',
    category: 'Tiền ăn'
  },
  {
    id: '5e887a1fbefd7938eea9c981',
    date: subDays(subHours(now, 5), 4).getTime(),
    amount: -150000,
    note: 'Mua gạo / khoản này chia 3',
    type: 'Chi tiêu',
    category: 'Tiền ăn'
  },
];

const useTransactions = (page, rowsPerPage) => {
  return useMemo(
    () => {
      return applyPagination(data, page, rowsPerPage);
    },
    [page, rowsPerPage]
  );
};

const useTransactionsIds = (transactions) => {
  return useMemo(
    () => {
      return transactions.map((transaction) => transaction.id);
    },
    [transactions]
  );
};

const Page = () => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const transactions = useTransactions(page, rowsPerPage);
  const transactionsIds = useTransactionsIds(transactions);
  const transactionsSelection = useSelection(transactionsIds);

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
          Transactions | Spending-Webapp
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
                  Transactions
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
                <PopupAddTransaction/>
              </div>
            </Stack>
            <TransactionsSearch />
            <TransactionsTable
              count={data.length}
              items={transactions}
              onDeselectAll={transactionsSelection.handleDeselectAll}
              onDeselectOne={transactionsSelection.handleDeselectOne}
              onPageChange={handlePageChange}
              onRowsPerPageChange={handleRowsPerPageChange}
              onSelectAll={transactionsSelection.handleSelectAll}
              onSelectOne={transactionsSelection.handleSelectOne}
              page={page}
              rowsPerPage={rowsPerPage}
              selected={transactionsSelection.selected}
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
