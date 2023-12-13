import PropTypes from 'prop-types';
import CurrencyDollarIcon from '@heroicons/react/24/solid/CurrencyDollarIcon';
import { Avatar, Card, CardContent, Stack, SvgIcon, Typography } from '@mui/material';

export const OverviewSave = (props) => {
  const { value, sx } = props;

  return (
    <Card sx={sx}>
      <CardContent>
        <Stack
          alignItems="center"
          // direction="row"
          justifyContent="space-between"
          spacing={3}
        >
          <Avatar
            sx={{
              backgroundColor: 'primary.main',
              height: 56,
              width: 56
            }}
          >
            <SvgIcon>
              <CurrencyDollarIcon />
            </SvgIcon>
          </Avatar>
          <Stack spacing={1}>
            <Typography
              color="text.secondary"
              variant="overline"
              textAlign="center"
            >
              Save
            </Typography>
            <Typography variant="h4">
              {value}
            </Typography>
          </Stack>
          {/* <Avatar
            sx={{
              backgroundColor: 'primary.main',
              height: 56,
              width: 56
            }}
          >
            <SvgIcon>
              <CurrencyDollarIcon />
            </SvgIcon>
          </Avatar> */}
        </Stack>
      </CardContent>
    </Card>
  );
};

OverviewSave.propTypes = {
  value: PropTypes.string,
  sx: PropTypes.object
};
