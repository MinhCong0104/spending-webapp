import { useCallback, useMemo, useState } from 'react';
import Head from 'next/head';
import { subDays, subHours } from 'date-fns';
import ArrowDownOnSquareIcon from '@heroicons/react/24/solid/ArrowDownOnSquareIcon';
import ArrowUpOnSquareIcon from '@heroicons/react/24/solid/ArrowUpOnSquareIcon';
import { Box, Button, Container, Stack, SvgIcon, Typography } from '@mui/material';

import { useSelection } from 'src/hooks/use-selection';
import { Layout as DashboardLayout } from 'src/layouts/dashboard/layout';
import { applyPagination } from 'src/utils/apply-pagination';

import { SaveTable } from 'src/sections/save/save-table';
import { SaveSearch } from 'src/sections/save/save-search';
import { PopupAddSave } from 'src/sections/save/save-add'; 

const now = new Date();

const data = [
  {
    id: '5e887ac47eed253091be10cb',
    account: 'Mua điện thoại',
    amount: 9000000,
    note: ''
  },
  {
    id: '5e887b209c28ac3dd97f6db5',
    account: 'Mua điện thoại',
    amount: 10000000,
    note: ''
  },
  {
    id: '5e86809283e28b96d2d38537',
    account: 'Tiết kiệm đề phòng sự cố',
    amount: 500000,
    note: '',
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
          Save | Spending-Webapp
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
                  Save
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
                <PopupAddSave/>
              </div>
            </Stack>
            <SaveSearch />
            <SaveTable
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
