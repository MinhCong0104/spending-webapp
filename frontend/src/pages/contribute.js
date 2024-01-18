import { useCallback, useMemo, useState } from 'react';
import Head from 'next/head';
import { subDays, subHours } from 'date-fns';
import ArrowDownOnSquareIcon from '@heroicons/react/24/solid/ArrowDownOnSquareIcon';
import ArrowUpOnSquareIcon from '@heroicons/react/24/solid/ArrowUpOnSquareIcon';
import { Box, Button, Container, Stack, SvgIcon, Typography } from '@mui/material';
import { useSelection } from 'src/hooks/use-selection';
import { Layout as DashboardLayout } from 'src/layouts/dashboard/layout';
import { applyPagination } from 'src/utils/apply-pagination';
import { PopupAddContribute } from 'src/sections/contribute/contribute-add';
import { ContributeTable } from 'src/sections/contribute/contribute-table';


const now = new Date();

const data = [
  {
    id: '5e887ac47eed253091be12cb',
    date: subDays(subHours(now, 7), 1).getTime(), //Input with default
    amount: 430000, //Input
    note: 'Đóng tiền mạng',
    from: 'Phương', //Select
    people: 'Phương, Công, Phú', //Select many
    amount_each: 144000, //Compute
    done: false, //Check with default false
  },
  {
    id: '5e887b209c28ac3dd97f7db5',
    date: subDays(subHours(now, 1), 2).getTime(),
    amount: -100000,
    note: 'Xem phim',
    from: 'Huyền',
    people: 'Huyền, Đạt, Công, Phương',
    amount_each: 25000,
    done: false,
  },
  {
    id: '5e887b209c28ac3dd97f7db5',
    date: subDays(subHours(now, 1), 2).getTime(),
    amount: 240000,
    note: 'Mua gạo, rau',
    from: 'Phú',
    people: 'Phú, Công, Phương',
    amount_each: 80000,
    done: false,
  },
  {
    id: '5e887b209c28ac3dd97f7db5',
    date: subDays(subHours(now, 1), 2).getTime(),
    amount: 450000,
    note: 'Đóng tiền điện',
    from: 'Phương',
    people: 'Phú, Công, Phương',
    amount_each: 150000,
    done: true,
  },
];


const useContribute = (page, rowsPerPage) => {
  return useMemo(
    () => {
      return applyPagination(data, page, rowsPerPage);
    },
    [page, rowsPerPage]
  );
};

const useContributeIds = (contribute) => {
  return useMemo(
    () => {
      return contribute.map((c) => c.id);
    },
    [contribute]
  );
};

const Page = () => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const contribute = useContribute(page, rowsPerPage);
  const contributeIds = useContributeIds(contribute);
  const contributeSelection = useSelection(contributeIds);

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
          Contribute | Spending-Webapp
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
                  Contribute
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
                <PopupAddContribute/>
              </div>
            </Stack>
            <ContributeSearch />
            <ContributeTable
              count={data.length}
              items={contribute}
              onDeselectAll={contributeSelection.handleDeselectAll}
              onDeselectOne={contributeSelection.handleDeselectOne}
              onPageChange={handlePageChange}
              onRowsPerPageChange={handleRowsPerPageChange}
              onSelectAll={contributeSelection.handleSelectAll}
              onSelectOne={contributeSelection.handleSelectOne}
              page={page}
              rowsPerPage={rowsPerPage}
              selected={contributeSelection.selected}
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
