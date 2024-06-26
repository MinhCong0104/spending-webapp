import PropTypes from 'prop-types';
import ListBulletIcon from '@heroicons/react/24/solid/ListBulletIcon';
import {
  Avatar,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Stack,
  SvgIcon,
  Typography
} from '@mui/material';

export const OverviewRemain = (props) => {
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
              backgroundColor: 'warning.main',
              height: 56,
              width: 56
            }}
          >
            <SvgIcon>
              <ListBulletIcon />
            </SvgIcon>
          </Avatar>
          <Stack spacing={1}>
            <Typography
              color="text.secondary"
              gutterBottom
              variant="overline"
              textAlign="center"
            >
              Remain
            </Typography>
            <Typography variant="h4">
              {value}
            </Typography>
          </Stack>
          {/* <Avatar
            sx={{
              backgroundColor: 'warning.main',
              height: 56,
              width: 56
            }}
          >
            <SvgIcon>
              <ListBulletIcon />
            </SvgIcon>
          </Avatar> */}
        </Stack>
        {/* <Box sx={{ mt: 3 }}>
          <LinearProgress
            value={value}
            variant="determinate"
          />
        </Box> */}
      </CardContent>
    </Card>
  );
};

OverviewRemain.propTypes = {
  value: PropTypes.string.isRequired,
  sx: PropTypes.object
};
