import PropTypes from 'prop-types';
import { format } from 'date-fns';
import { Box, Card, Checkbox, Stack, Table, TableBody, TableCell, TableHead, TablePagination, TableRow, Typography } from '@mui/material';
import { Scrollbar } from 'src/components/scrollbar';
import { getInitials } from 'src/utils/get-initials';

export const ContributeTable = (props) => {
  const {
    count = 0,
    items = [],
    onDeselectAll,
    onDeselectOne,
    onPageChange = () => {},
    onRowsPerPageChange,
    onSelectAll,
    onSelectOne,
    page = 0,
    rowsPerPage = 0,
    selected = []
  } = props;

  const selectedSome = (selected.length > 0) && (selected.length < items.length);
  const selectedAll = (items.length > 0) && (selected.length === items.length);

  return (
    <Card>
      <Scrollbar>
        <Box sx={{ minWidth: 800 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selectedAll}
                    indeterminate={selectedSome}
                    onChange={(event) => {
                      if (event.target.checked) {
                        onSelectAll?.();
                      } else {
                        onDeselectAll?.();
                      }
                    }}
                  />
                </TableCell>
                <TableCell>
                  Date
                </TableCell>
                <TableCell>
                  Person pay money
                </TableCell>
                <TableCell>
                  Anount
                </TableCell>
                <TableCell>
                  People contribute
                </TableCell>
                <TableCell>
                  Note
                </TableCell>
                <TableCell>
                  amount_each
                </TableCell>
                <TableCell>
                  Note
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map((contribute) => {
                const isSelected = selected.includes(contribute.id);
                const date = format(contribute.date, 'dd/MM/yyyy');

                return (
                  <TableRow
                    hover
                    key={contribute.id}
                    selected={isSelected}
                  >
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={isSelected}
                        onChange={(event) => {
                          if (event.target.checked) {
                            onSelectOne?.(contribute.id);
                          } else {
                            onDeselectOne?.(contribute.id);
                          }
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      {date}
                    </TableCell>
                    <TableCell>
                      {contribute.from}
                    </TableCell>
                    <TableCell>
                      {contribute.amount}
                    </TableCell>
                    <TableCell>
                      {contribute.people}
                    </TableCell>
                    <TableCell>
                      {contribute.note}
                    </TableCell>
                    <TableCell>
                      {contribute.amount_each}
                    </TableCell>
                    <TableCell>
                      {contribute.done}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </Box>
      </Scrollbar>
      <TablePagination
        component="div"
        count={count}
        onPageChange={onPageChange}
        onRowsPerPageChange={onRowsPerPageChange}
        page={page}
        rowsPerPage={rowsPerPage}
        rowsPerPageOptions={[5, 10, 20, 50]}
      />
    </Card>
  );
};

contributeTable.propTypes = {
  count: PropTypes.number,
  items: PropTypes.array,
  onDeselectAll: PropTypes.func,
  onDeselectOne: PropTypes.func,
  onPageChange: PropTypes.func,
  onRowsPerPageChange: PropTypes.func,
  onSelectAll: PropTypes.func,
  onSelectOne: PropTypes.func,
  page: PropTypes.number,
  rowsPerPage: PropTypes.number,
  selected: PropTypes.array
};
